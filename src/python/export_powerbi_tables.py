"""
export_powerbi_tables.py
========================
Pipeline reproducible para la generación y exportación de tablas dimensionales
y de hechos destinadas al modelo semántico de Microsoft Power BI en el proyecto
Energy Demand Intelligence.

Fase 1: Preparación y estructuración analítica de datos.
Autor: Energy Demand Intelligence Team
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

# -----------------------------------------------------------------------------
# 1. Rutas y configuración general
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed" / "Tetouan_Clean_v1.csv"
OUTPUTS_FORECASTS = PROJECT_ROOT / "outputs" / "forecasts"
OUTPUTS_POWERBI = PROJECT_ROOT / "outputs" / "powerbi"

RANDOM_SEED = 42
N_BOOTSTRAP_SIMS = 1000

ZONES = ["zone_1_load", "zone_2_load", "zone_3_load"]
ZONE_METADATA = {
    "zone_1_load": {"nombre": "Zone 1 - Quads", "alias": "Quads", "orden": 1},
    "zone_2_load": {"nombre": "Zone 2 - Smir", "alias": "Smir", "orden": 2},
    "zone_3_load": {"nombre": "Zone 3 - Boussafou", "alias": "Boussafou", "orden": 3},
}

FEATURE_COLUMNS = [
    "target_hour", "target_day_of_week", "target_month", "target_is_weekend", "lead",
    "last_observed", "lag_24_at_origin", "lag_168_at_origin",
    "mean_prev_24", "mean_prev_168", "seasonal_lag",
]


# -----------------------------------------------------------------------------
# 2. Funciones de extracción de características y entrenamiento
# -----------------------------------------------------------------------------
def direct_features(values, index, origin_idx, horizon):
    """Construye las características disponibles en el origen para predecir horizonte."""
    target_idx = np.arange(origin_idx + 1, origin_idx + horizon + 1)
    target_times = index[target_idx]
    return pd.DataFrame({
        "target_hour": target_times.hour,
        "target_day_of_week": target_times.dayofweek,
        "target_month": target_times.month,
        "target_is_weekend": (target_times.dayofweek >= 5).astype(int),
        "lead": np.arange(1, horizon + 1),
        "last_observed": values[origin_idx],
        "lag_24_at_origin": values[origin_idx - 24],
        "lag_168_at_origin": values[origin_idx - 168],
        "mean_prev_24": values[origin_idx - 23:origin_idx + 1].mean(),
        "mean_prev_168": values[origin_idx - 167:origin_idx + 1].mean(),
        "seasonal_lag": values[target_idx - horizon],
    }, index=target_times)[FEATURE_COLUMNS]


def direct_training_set(values, index, train_end_idx, horizon, origin_step, first_origin_idx):
    """Construye la matriz de entrenamiento con orígenes periódicos."""
    x_parts, y_parts = [], []
    last_origin_idx = train_end_idx - horizon
    for origin_idx in range(first_origin_idx, last_origin_idx + 1, origin_step):
        x_parts.append(direct_features(values, index, origin_idx, horizon))
        y_parts.append(values[origin_idx + 1:origin_idx + horizon + 1])
    return pd.concat(x_parts), np.concatenate(y_parts)


# -----------------------------------------------------------------------------
# 3. Flujo Principal
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Iniciando generación de tablas para Power BI (Fase 1)")
    print("=" * 70)

    OUTPUTS_POWERBI.mkdir(parents=True, exist_ok=True)

    # 3.1. Carga de datos procesados
    if not DATA_PROCESSED.exists():
        raise FileNotFoundError(f"No se encontró el dataset en {DATA_PROCESSED}")

    print(f"\n1. Cargando datos desde {DATA_PROCESSED.name}...")
    df_raw = pd.read_csv(DATA_PROCESSED)
    df_raw["datetime"] = pd.to_datetime(df_raw["datetime"])
    
    # Agregación horaria mediante media
    hourly = df_raw.set_index("datetime").resample("h").mean()
    print(f"   Horas observadas: {len(hourly):,} ({hourly.index.min()} a {hourly.index.max()})")

    # Particiones cronológicas idénticas a CRISP-DM
    last_hour = hourly.index.max()
    test_start = last_hour.normalize() - pd.Timedelta(days=27)
    validation_start = test_start - pd.Timedelta(days=28)
    train_end = validation_start - pd.Timedelta(hours=1)
    validation_end = test_start - pd.Timedelta(hours=1)

    train_data = hourly.loc[:train_end]
    validation_data = hourly.loc[validation_start:validation_end]
    test_data = hourly.loc[test_start:last_hour]

    print(f"   Partición Entrenamiento: {len(train_data):,} horas ({train_data.index.min()} -> {train_data.index.max()})")
    print(f"   Partición Validación:    {len(validation_data):,} horas ({validation_data.index.min()} -> {validation_data.index.max()})")
    print(f"   Partición Prueba (Test): {len(test_data):,} horas ({test_data.index.min()} -> {test_data.index.max()})")

    # 3.2. Calibración de Residuos de Validación
    print("\n2. Evaluando modelos en validación para calcular cuantiles empíricos...")
    
    train_end_idx = hourly.index.get_loc(train_data.index.max())
    val_start_idx = hourly.index.get_loc(validation_data.index.min())
    val_end_idx = hourly.index.get_loc(validation_data.index.max())

    model_factories = {
        "Random Forest": lambda: RandomForestRegressor(
            n_estimators=80, min_samples_leaf=5, random_state=RANDOM_SEED, n_jobs=1
        ),
        "HistGradientBoosting": lambda: HistGradientBoostingRegressor(
            max_iter=100, learning_rate=0.06, max_leaf_nodes=15,
            l2_regularization=1.0, random_state=RANDOM_SEED
        ),
    }

    horizons_cfg = [
        {"horizonte": "24 horas", "steps": 24, "origin_step": 24, "first_origin": 24 * 7 + 23, "lead_bins": [0, 6, 12, 18, 24], "lead_labels": ["1-6h", "7-12h", "13-18h", "19-24h"]},
        {"horizonte": "7 días", "steps": 168, "origin_step": 168, "first_origin": 167, "lead_bins": [0, 48, 96, 168], "lead_labels": ["1-48h", "49-96h", "97-168h"]},
    ]

    val_records = []
    val_trajectories_sync = {} # Clave: (horizonte, modelo) -> array de shape (N_origenes, steps, 3_zonas)

    for h_cfg in horizons_cfg:
        h_name = h_cfg["horizonte"]
        steps = h_cfg["steps"]
        origin_step = h_cfg["origin_step"]
        first_origin = h_cfg["first_origin"]
        
        last_val_start_idx = val_end_idx - steps + 1
        target_starts_val = list(range(val_start_idx, last_val_start_idx + 1, steps))

        # 1. Modelo Estacional (Baseline) para todas las zonas
        for target_start_idx in target_starts_val:
            origin_idx = target_start_idx - 1
            fecha_origen = hourly.index[origin_idx]
            target_idx = np.arange(target_start_idx, target_start_idx + steps)
            
            for zone in ZONES:
                vals = hourly[zone].to_numpy()
                actual = vals[target_idx]
                seasonal_pred = vals[target_idx - steps]
                errors = actual - seasonal_pred
                
                for lead_i, (ts, y_true, y_pred, err) in enumerate(zip(hourly.index[target_idx], actual, seasonal_pred, errors), start=1):
                    val_records.append({
                        "horizonte": h_name,
                        "zona": zone,
                        "modelo": "Estacional",
                        "fecha_origen": fecha_origen,
                        "lead_horas": lead_i,
                        "datetime": ts,
                        "real": y_true,
                        "predicho": y_pred,
                        "error": err
                    })

        # 2. Modelos ML candidatos
        for zone in ZONES:
            vals = hourly[zone].to_numpy()
            x_train, y_train = direct_training_set(
                vals, hourly.index, train_end_idx, steps, origin_step, first_origin
            )

            # Entrenar modelos según aplique
            # HistGradientBoosting para Zone 2 (24h) y Random Forest para Zone 3 (7d)
            models_to_run = []
            if h_name == "24 horas":
                models_to_run.append("HistGradientBoosting")
            elif h_name == "7 días":
                models_to_run.append("Random Forest")

            for m_name in models_to_run:
                model = model_factories[m_name]().fit(x_train, y_train)

                for target_start_idx in target_starts_val:
                    origin_idx = target_start_idx - 1
                    fecha_origen = hourly.index[origin_idx]
                    target_idx = np.arange(target_start_idx, target_start_idx + steps)
                    x_val = direct_features(vals, hourly.index, origin_idx, steps)
                    preds = model.predict(x_val)
                    actual = vals[target_idx]
                    errors = actual - preds

                    for lead_i, (ts, y_true, y_pred, err) in enumerate(zip(hourly.index[target_idx], actual, preds, errors), start=1):
                        val_records.append({
                            "horizonte": h_name,
                            "zona": zone,
                            "modelo": m_name,
                            "fecha_origen": fecha_origen,
                            "lead_horas": lead_i,
                            "datetime": ts,
                            "real": y_true,
                            "predicho": y_pred,
                            "error": err
                        })

    df_val_errors = pd.DataFrame(val_records)
    print(f"   Observaciones residuales en validación generadas: {len(df_val_errors):,}")

    # Asignar bins de tiempo de anticipación (lead-time bins)
    quantile_calibrations = {}
    for h_cfg in horizons_cfg:
        h_name = h_cfg["horizonte"]
        bins = h_cfg["lead_bins"]
        labels = h_cfg["lead_labels"]

        sub = df_val_errors[df_val_errors["horizonte"] == h_name].copy()
        sub["lead_bin"] = pd.cut(sub["lead_horas"], bins=bins, labels=labels, right=True)

        for (z, m), group in sub.groupby(["zona", "modelo"]):
            for bin_label, bin_group in group.groupby("lead_bin", observed=False):
                errs = bin_group["error"].values
                q10 = np.quantile(errs, 0.10)
                q90 = np.quantile(errs, 0.90)
                quantile_calibrations[(h_name, z, m, bin_label)] = (q10, q90, len(errs))

    print(f"   Cuantiles empíricos (q10, q90) calibrados: {len(quantile_calibrations)} grupos.")

    # 3.3. Construcción de Fact_Pronostico sobre Test
    print("\n3. Construyendo Fact_Pronostico sobre el conjunto Test de Diciembre...")
    
    # Cargar predicciones oficiales de test desde dashboard_forecast_predictions.csv
    df_test_preds = pd.read_csv(OUTPUTS_FORECASTS / "dashboard_forecast_predictions.csv")
    df_test_preds["datetime"] = pd.to_datetime(df_test_preds["datetime"])

    # Calcular P95 histórico rodante de los 14 días previos a cada origen
    # En test hay:
    # 24h -> 28 orígenes (inicios diarios: 2017-12-03 00:00:00 a 2017-12-30 00:00:00)
    # 7d  -> 4 orígenes  (inicios semanales: 2017-12-03 00:00:00, 2017-12-10, 2017-12-17, 2017-12-24)
    
    # Modelo seleccionado por validación:
    # 24h: zone_1 -> Estacional, zone_2 -> HistGradientBoosting, zone_3 -> Estacional
    # 7d:  zone_1 -> Estacional, zone_2 -> Estacional, zone_3 -> Random Forest
    selected_models_map = {
        ("24 horas", "zone_1_load"): "Estacional",
        ("24 horas", "zone_2_load"): "HistGradientBoosting",
        ("24 horas", "zone_3_load"): "Estacional",
        ("7 días", "zone_1_load"): "Estacional",
        ("7 días", "zone_2_load"): "Estacional",
        ("7 días", "zone_3_load"): "Random Forest",
    }

    fact_pronostico_rows = []

    # Iterar por grupo de horizonte, zona y modelo
    for (h_name, z_name, m_name), grp in df_test_preds.groupby(["horizonte", "zona", "modelo"]):
        steps = 24 if h_name == "24 horas" else 168
        bins = [0, 6, 12, 18, 24] if h_name == "24 horas" else [0, 48, 96, 168]
        labels = ["1-6h", "7-12h", "13-18h", "19-24h"] if h_name == "24 horas" else ["1-48h", "49-96h", "97-168h"]

        is_selected = (selected_models_map.get((h_name, z_name)) == m_name)

        # Ordenar cronológicamente
        grp_sorted = grp.sort_values("datetime").reset_index(drop=True)
        n_rows = len(grp_sorted)
        n_origins = n_rows // steps

        for i in range(n_origins):
            origin_block = grp_sorted.iloc[i * steps : (i + 1) * steps].copy()
            target_start = origin_block["datetime"].iloc[0]
            fecha_origen = target_start - pd.Timedelta(hours=1)

            # Calcular P95 histórico de 14 días (336 horas) fijo en fecha_origen
            origin_idx = hourly.index.get_loc(fecha_origen)
            p95_history = hourly[z_name].iloc[origin_idx - 335 : origin_idx + 1]
            p95_fixed = p95_history.quantile(0.95)

            lead_hours = np.arange(1, steps + 1)
            lead_bins = pd.cut(lead_hours, bins=bins, labels=labels, right=True)

            for lead, b_label, (_, row) in zip(lead_hours, lead_bins, origin_block.iterrows()):
                # Obtener calibración de validación
                calib = quantile_calibrations.get((h_name, z_name, m_name, b_label))
                if calib is not None:
                    q10, q90, _ = calib
                else:
                    # Fallback si no hubiese bin (no debe ocurrir)
                    q10, q90 = 0.0, 0.0

                pred_inf_80 = row["predicho"] + q10
                pred_sup_80 = row["predicho"] + q90

                fact_pronostico_rows.append({
                    "fecha_origen": fecha_origen,
                    "lead_horas": int(lead),
                    "datetime": row["datetime"],
                    "zona_id": z_name,
                    "horizonte": h_name,
                    "modelo": m_name,
                    "es_modelo_seleccionado": is_selected,
                    "real": row["real"],
                    "predicho": row["predicho"],
                    "predicho_inf_80": pred_inf_80,
                    "predicho_sup_80": pred_sup_80,
                    "threshold_p95": p95_fixed
                })

    df_fact_pronostico = pd.DataFrame(fact_pronostico_rows)
    print(f"   Filas en Fact_Pronostico generadas: {len(df_fact_pronostico):,}")

    # 3.4. Auditoría de Cobertura y Amplitud en Test
    print("\n4. Auditando Cobertura y Amplitud de los Intervalos Predictivos del 80 % en Test...")
    audit_results = []
    
    for (h_name, z_name, m_name), grp in df_fact_pronostico.groupby(["horizonte", "zona_id", "modelo"]):
        covered = (grp["real"] >= grp["predicho_inf_80"]) & (grp["real"] <= grp["predicho_sup_80"])
        coverage_pct = covered.mean() * 100
        mean_width = (grp["predicho_sup_80"] - grp["predicho_inf_80"]).mean()
        is_sel = grp["es_modelo_seleccionado"].iloc[0]

        audit_results.append({
            "Horizonte": h_name,
            "Zona": ZONE_METADATA[z_name]["alias"],
            "Modelo": m_name,
            "Seleccionado": is_sel,
            "Cobertura_Test_Pct": round(coverage_pct, 2),
            "Amplitud_Media": round(mean_width, 1),
            "Observaciones": len(grp)
        })

    df_audit = pd.DataFrame(audit_results)
    print(df_audit.to_string(index=False))

    # 3.5. Simulación de Probabilidad de Pico vía Block Bootstrap Sincronizado
    # Metodología:
    # - Tamaño de bloque: H pasos (H = 24 horas para horizonte diario; H = 168 horas para horizonte semanal).
    # - Muestreo sincronizado: Para cada simulación b (de 1 a 1.000), se extrae un único índice temporal inicial
    #   s_b en el historial de validación. Dicho índice se aplica idénticamente a las tres zonas, preservando de
    #   manera exacta la covarianza espacial (interdependencia entre Quads, Smir y Boussafou).
    # - Conservación de la estructura de anticipación: Al extraer un bloque continuo [s_b, s_b + H], la posición
    #   relativa de cada hora t (lead-time) y la autocorrelación residual intra-bloque se respetan fielmente.
    # - Nota metodológica: Para el horizonte de 24 horas se evalúan 28 orígenes diarios de test; para el horizonte
    #   de 7 días se evalúan únicamente los 4 orígenes semanales disponibles en diciembre de 2017, por lo que las
    #   probabilidades semanales resultantes deben interpretarse como hallazgos experimentales de esa muestra limitada.
    print(f"\n5. Ejecutando {N_BOOTSTRAP_SIMS:,} simulaciones mediante Block Bootstrap sincronizado interzonal...")
    np.random.seed(RANDOM_SEED)

    # Preparar matriz de residuos de validación sincronizados
    # Para cada horizonte y modelo seleccionado, extraemos los residuos de validación alineados por timestamp
    # Para 24h, usamos los 28 bloques de 24h de validación (o bloques deslizantes de longitud H)
    fact_prob_rows = []

    # Extraemos las predicciones sobre test de los modelos para cada origen
    # Obtenemos los orígenes únicos en test por horizonte
    for h_cfg in horizons_cfg:
        h_name = h_cfg["horizonte"]
        steps = h_cfg["steps"]

        # Residuos de validación sincronizados de las tres zonas
        # Filtramos las predicciones de validación de los modelos seleccionados
        val_sync_dict = {}
        for z in ZONES:
            m_sel = selected_models_map[(h_name, z)]
            z_val = df_val_errors[(df_val_errors["horizonte"] == h_name) & 
                                  (df_val_errors["zona"] == z) & 
                                  (df_val_errors["modelo"] == m_sel)].sort_values(["fecha_origen", "lead_horas"])
            val_sync_dict[z] = z_val

        # Obtenemos los bloques de validación sincronizados
        # Hay 28 orígenes para 24h y 4 orígenes para 7d
        # Para enriquecer el remuestreo respetando la autocorrelación continua de las 672 horas de validación,
        # construimos una matriz continua de residuos horarios de validación de shape (672, 3)
        # uniendo los residuos observados en validación.
        val_dates = validation_data.index
        matrix_val_resids = np.zeros((len(val_dates), len(ZONES)))
        
        for z_idx, z in enumerate(ZONES):
            # Serie real - serie estacional/modelo
            m_sel = selected_models_map[(h_name, z)]
            # Usamos los residuos de df_val_errors
            sub_res = df_val_errors[(df_val_errors["horizonte"] == h_name) & 
                                    (df_val_errors["zona"] == z) & 
                                    (df_val_errors["modelo"] == m_sel)]
            # Mapear error por datetime
            err_map = sub_res.set_index("datetime")["error"]
            matrix_val_resids[:, z_idx] = err_map.reindex(val_dates).fillna(0.0).values

        n_val_hours = len(matrix_val_resids)
        max_start_idx = n_val_hours - steps

        if max_start_idx <= 0:
            bootstrap_start_indices = np.zeros(N_BOOTSTRAP_SIMS, dtype=int)
        else:
            # 1.000 índices de inicio sincronizados muestreados con reemplazo
            bootstrap_start_indices = np.random.randint(0, max_start_idx + 1, size=N_BOOTSTRAP_SIMS)

        # Ahora evaluamos para cada fecha_origen de test
        df_sub_test = df_fact_pronostico[df_fact_pronostico["horizonte"] == h_name]
        unique_origins = df_sub_test["fecha_origen"].drop_duplicates().sort_values()

        for f_orig in unique_origins:
            orig_data = df_sub_test[df_sub_test["fecha_origen"] == f_orig]

            orig_zone_sims = {}
            orig_zone_exceeded = {}
            orig_zone_meta = {}

            for z_idx, z in enumerate(ZONES):
                m_sel = selected_models_map[(h_name, z)]
                z_data = orig_data[(orig_data["zona_id"] == z) & (orig_data["modelo"] == m_sel)].sort_values("lead_horas")
                
                if len(z_data) != steps:
                    continue

                point_forecast = z_data["predicho"].values
                p95_fixed = z_data["threshold_p95"].iloc[0]
                lead_datetimes = z_data["datetime"].dt.strftime("%H:00").values

                # Matriz de simulaciones: shape (N_BOOTSTRAP_SIMS, steps)
                simulated_trajectories = np.zeros((N_BOOTSTRAP_SIMS, steps))
                for sim_i, s_idx in enumerate(bootstrap_start_indices):
                    sim_err = matrix_val_resids[s_idx : s_idx + steps, z_idx]
                    simulated_trajectories[sim_i, :] = point_forecast + sim_err

                # Análisis de eventos elevados en las trayectorias de la zona
                max_peaks = np.max(simulated_trajectories, axis=1) # shape (1000,)
                peak_exceeded = (max_peaks >= p95_fixed)
                prob_peak = np.mean(peak_exceeded)

                # Hora del pico en las trayectorias
                peak_lead_indices = np.argmax(simulated_trajectories, axis=1) # shape (1000,)
                modal_lead_idx = pd.Series(peak_lead_indices).mode().iloc[0]
                hora_pico_esperado = lead_datetimes[modal_lead_idx]

                # Horas elevadas promedio
                hours_exceeded_per_sim = np.sum(simulated_trajectories >= p95_fixed, axis=1)
                mean_elevated_hours = int(round(np.mean(hours_exceeded_per_sim)))
                mean_peak_val = np.mean(max_peaks)

                orig_zone_sims[z] = simulated_trajectories
                orig_zone_exceeded[z] = peak_exceeded
                orig_zone_meta[z] = {
                    "m_sel": m_sel,
                    "prob_peak": prob_peak,
                    "mean_peak_val": mean_peak_val,
                    "hora_pico_esperado": hora_pico_esperado,
                    "mean_elevated_hours": mean_elevated_hours
                }

            if len(orig_zone_exceeded) == len(ZONES):
                # Probabilidad conjunta de red: P(al menos una zona supera P95 durante H)
                # En cada simulación s_i, se comprueba si la zona 1, la zona 2 o la zona 3 superó su umbral P95
                net_exceeded_any = np.zeros(N_BOOTSTRAP_SIMS, dtype=bool)
                for z in ZONES:
                    net_exceeded_any = net_exceeded_any | orig_zone_exceeded[z]
                prob_red_conjunta = float(np.mean(net_exceeded_any))

                for z in ZONES:
                    meta = orig_zone_meta[z]
                    fact_prob_rows.append({
                        "fecha_origen": f_orig,
                        "zona_id": z,
                        "horizonte": h_name,
                        "modelo": meta["m_sel"],
                        "es_modelo_seleccionado": True,
                        "probabilidad_al_menos_un_pico": round(float(meta["prob_peak"]), 4),
                        "probabilidad_red_al_menos_un_pico": round(float(prob_red_conjunta), 4),
                        "pico_esperado_max": round(float(meta["mean_peak_val"]), 1),
                        "hora_pico_esperado": meta["hora_pico_esperado"],
                        "horas_elevadas_esperadas": meta["mean_elevated_hours"],
                        "num_simulaciones": N_BOOTSTRAP_SIMS
                    })

    df_fact_prob_pico = pd.DataFrame(fact_prob_rows)
    print(f"   Filas en Fact_Probabilidad_Pico generadas: {len(df_fact_prob_pico):,}")
    print("   Resumen de probabilidades de pico simuladas:")
    print(df_fact_prob_pico.groupby(["horizonte", "zona_id"])["probabilidad_al_menos_un_pico"].describe().to_string())

    # 3.6. Construcción de Fact_Eventos_Clasificacion
    print("\n6. Construyendo Fact_Eventos_Clasificacion a partir de los resultados de clasificación...")
    df_cls = pd.read_csv(OUTPUTS_FORECASTS / "dashboard_classification_predictions.csv")
    df_cls["datetime"] = pd.to_datetime(df_cls["datetime"])

    fact_eventos_cols = [
        "datetime", "zona", "modelo", "estrategia", "real", "probabilidad",
        "umbral_probabilidad", "threshold_p95", "prediccion", "estado_predicho", "estado_real"
    ]
    df_fact_eventos = df_cls[fact_eventos_cols].rename(columns={"zona": "zona_id"})
    print(f"   Filas en Fact_Eventos_Clasificacion: {len(df_fact_eventos):,}")

    # 3.7. Construcción de Fact_Demanda_Horaria (Serie completa 2017)
    print("\n7. Construyendo Fact_Demanda_Horaria (Serie completa continua de 2017)...")
    fact_demanda_rows = []
    
    for z in ZONES:
        sub_h = pd.DataFrame({
            "datetime": hourly.index,
            "zona_id": z,
            "demanda": hourly[z].values,
            "temperatura": hourly["temperature"].values,
            "humedad": hourly["humidity"].values,
            "viento": hourly["wind_speed"].values
        })
        fact_demanda_rows.append(sub_h)

    df_fact_demanda = pd.concat(fact_demanda_rows, ignore_index=True)
    print(f"   Filas en Fact_Demanda_Horaria: {len(df_fact_demanda):,} (8.736 horas x 3 zonas)")

    # 3.8. Construcción de Tablas Dimensionales
    print("\n8. Construyendo tablas dimensionales...")
    
    # Dim_Zona
    df_dim_zona = pd.DataFrame([
        {
            "zona_id": z,
            "zona_nombre": ZONE_METADATA[z]["nombre"],
            "zona_alias": ZONE_METADATA[z]["alias"],
            "orden": ZONE_METADATA[z]["orden"]
        }
        for z in ZONES
    ])

    # Dim_Calendario
    unique_dates = hourly.index
    dias_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    
    df_dim_calendario = pd.DataFrame({
        "datetime": unique_dates,
        "fecha": unique_dates.date,
        "hora": unique_dates.hour,
        "hora_str": unique_dates.strftime("%H:00"),
        "dia_semana": unique_dates.dayofweek + 1, # 1=Lunes, 7=Domingo
        "dia_nombre": [dias_es[d] for d in unique_dates.dayofweek],
        "mes_nombre": [meses_es[m] for m in unique_dates.month],
        "es_fin_semana": (unique_dates.dayofweek >= 5).astype(bool)
    })

    # Dim_Horizonte
    df_dim_horizonte = pd.DataFrame([
        {"horizonte": "24 horas", "horas_horizonte": 24, "orden": 1},
        {"horizonte": "7 días", "horas_horizonte": 168, "orden": 2}
    ])

    # Dim_Ventana_Historica
    df_dim_ventana = pd.DataFrame([
        {"ventana_id": "24h", "ventana_nombre": "24 horas", "horas_atras": 24, "orden": 1},
        {"ventana_id": "1mes", "ventana_nombre": "1 mes", "horas_atras": 720, "orden": 2},
        {"ventana_id": "todo", "ventana_nombre": "Todo el periodo", "horas_atras": 8760, "orden": 3}
    ])

    # Dim_Fecha_Origen
    # Construida a partir de los orígenes únicos evaluados en Fact_Pronostico y Fact_Probabilidad_Pico
    unique_origins_series = pd.Series(
        list(set(df_fact_pronostico["fecha_origen"]).union(set(df_fact_prob_pico["fecha_origen"])))
    ).sort_values().reset_index(drop=True)
    
    unique_origins_dt = pd.to_datetime(unique_origins_series)
    meses_abr_es = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun", 7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}
    
    df_dim_fecha_origen = pd.DataFrame({
        "fecha_origen": unique_origins_series,
        "fecha": unique_origins_dt.dt.date,
        "hora": unique_origins_dt.dt.hour,
        "hora_str": unique_origins_dt.dt.strftime("%H:00"),
        "etiqueta_origen": [
            f"{dt.strftime('%d')} {meses_abr_es[dt.month]} {dt.year} · {dt.strftime('%H:00')}"
            for dt in unique_origins_dt
        ],
        "dia_semana": unique_origins_dt.dt.dayofweek + 1,
        "dia_nombre": [dias_es[d] for d in unique_origins_dt.dt.dayofweek],
        "mes_nombre": [meses_es[m] for m in unique_origins_dt.dt.month],
        "orden": np.arange(1, len(unique_origins_series) + 1)
    })
    print(f"   Filas en Dim_Fecha_Origen: {len(df_dim_fecha_origen)} orígenes únicos.")

    # 3.9. Exportación a CSV
    print(f"\n9. Exportando tablas definitivas a {OUTPUTS_POWERBI}...")
    
    tables_to_export = {
        "Dim_Zona.csv": df_dim_zona,
        "Dim_Calendario.csv": df_dim_calendario,
        "Dim_Horizonte.csv": df_dim_horizonte,
        "Dim_Ventana_Historica.csv": df_dim_ventana,
        "Dim_Fecha_Origen.csv": df_dim_fecha_origen,
        "Fact_Demanda_Horaria.csv": df_fact_demanda,
        "Fact_Pronostico.csv": df_fact_pronostico,
        "Fact_Probabilidad_Pico.csv": df_fact_prob_pico,
        "Fact_Eventos_Clasificacion.csv": df_fact_eventos
    }

    manifest = []
    for filename, df in tables_to_export.items():
        file_path = OUTPUTS_POWERBI / filename
        df.to_csv(file_path, index=False, encoding="utf-8")
        manifest.append({
            "Archivo": filename,
            "Filas": len(df),
            "Columnas": len(df.columns),
            "Tamano_KB": round(file_path.stat().st_size / 1024, 1)
        })

    df_manifest = pd.DataFrame(manifest)
    print("\nInventario de tablas exportadas:")
    print(df_manifest.to_string(index=False))

    # Guardar reporte de auditoría de cobertura
    df_audit.to_csv(OUTPUTS_POWERBI / "Reporte_Auditoria_Intervalos_80.csv", index=False)
    print("\nAuditoría guardada en outputs/powerbi/Reporte_Auditoria_Intervalos_80.csv")

    print("\n" + "=" * 70)
    print("FASE 1 COMPLETADA CON ÉXITO")
    print("=" * 70)


if __name__ == "__main__":
    main()
