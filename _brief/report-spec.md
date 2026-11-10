# Report Spec: Energy Demand Intelligence

## Report identity
- Report name: Energy Demand Intelligence - Tétouan Grid Monitoring & Forecast (Prototipo Histórico 2017)
- Semantic model: Energy_Demand_Intelligence.SemanticModel
- Audience: Ingenieros de operación de red, analistas de demanda eléctrica y planificadores energéticos.
- Primary purpose: Monitorear la demanda histórica observada en 2017, evaluar pronósticos horarios a 24 horas y 7 días con bandas de incertidumbre al 80% (vía cuantiles empíricos), y anticipar la probabilidad de eventos de demanda elevada ($\ge P95$) mediante simulación de trayectorias en las tres zonas de Tétouan.
- Delivery target: Local PBIP en `powerbi/Energy_Demand_Intelligence.pbip` (para Power BI Desktop local).

## Semantic model binding
- Entry mode: Local Model
- Workspace name: N/A (Local)
- Workspace ID: N/A (Local)
- Model name: Energy_Demand_Intelligence
- Model ID: N/A (Local)
- connectionString: byPath ../Energy_Demand_Intelligence.SemanticModel

## User decisions and constraints
- Scope: Dashboard operativo y analítico en una única página panorámica (16:9, 1920 x 1080 FHD) estructurado como un prototipo histórico basado exclusivamente en los registros de 2017 de Tétouan.
- Page count: 1 página ("Demanda Eléctrica de Tétouan").
- Interactivity:
  - Slicer vertical de zona (Todas las zonas, Zone 1 - Quads, Zone 2 - Smir, Zone 3 - Boussafou) con filtrado cruzado bidireccional.
  - Slicer de horizonte de pronóstico (24 horas, 7 días).
  - Slicer de ventana histórica temporal adaptada al prototipo histórico: "24 horas", "1 mes" y "Todo el periodo" (período completo de 364 días disponible). Opciones de "1 año" (móvil) y "5 años" documentadas como no aplicables al dataset de 2017.
  - Selección de puntos en la serie temporal para actualizar la tarjeta de detalle técnico puntual.
  - Sincronización entre la tabla de eventos de alerta y el gráfico temporal.
- Design direction: Plataforma profesional de inteligencia energética moderna (estilo Command Center / Energy Intelligence Platform), paleta azul técnico (#0A2540, #0052CC) con acentos de advertencia (#D97706, #DC2626) y estados normales (#059669), fondo limpio suave (#F4F6F9) y tarjetas blancas elevadas con sombras sutiles y bordes limpios.
- Publishing: Local PBIP únicamente; prohibido publicar en la nube o Fabric sin aprobación explícita.
- Tooling: PBIP / PBIR local con especificación TMDL para el modelo y validación mediante `powerbi-report-author` CLI.
- Model edit permissions: Autorizado a crear tablas dimensionales y tablas de hechos en `outputs/powerbi/` y registrarlas en TMDL sin alterar los datos originales de `data/raw/` o `data/processed/`.
- Accessibility: Contraste WCAG AA, tipografía Segoe UI con alineación tabular para números, diferenciación por forma y estilo de línea (continua para real/pronóstico, segmentada para P95, sombreado para banda 80%) y textos alternativos descriptivos.

## Methodological rules & data caveats
1. **Separación entre backtesting y forecasting operativo:**
   - El dashboard se identifica en todo momento como un **prototipo histórico de 2017**; las predicciones corresponden a una evaluación fuera de muestra (backtesting rolling-origin de diciembre de 2017) y no a un pronóstico en tiempo real emitido hoy.
   - La fecha de corte y última actualización visible es el `30 dic 2017 · 23:00` (último día observado del dataset UCI).
   - La integración de una futura fuente operativa reciente de demanda se documenta como una fase técnica independiente y de baja probabilidad de consecución en el corto plazo.
2. **Intervalos predictivos del 80% mediante cuantiles empíricos:**
   - Calculados estrictamente a partir de los errores residuales del conjunto de validación ($e = \text{real} - \text{predicho}$):
     - $\text{Límite inferior} = \text{pronóstico} + q_{0.10}(e)$
     - $\text{Límite superior} = \text{pronóstico} + q_{0.90}(e)$
   - Prohibido combinar este método no paramétrico con la aproximación Gaussiana $\pm 1.28 \sigma$.
   - Calibración segmentada por `zona`, `modelo`, `horizonte` y agrupaciones de tiempo de anticipación (`lead_horas` en bins: e.g. 1-6h, 7-12h, 13-18h, 19-24h para 24h; 1-2d, 3-4d, 5-7d para 7 días) para garantizar cuantiles muestrales robustos.
   - Los datos del conjunto de prueba (diciembre 2017) se utilizan exclusivamente para auditar la cobertura empírica y la amplitud del intervalo, sin usarse jamás para calibrar los cuantiles.
   - La cobertura observada en Quads a 24 horas (77,68 %) se describe con prudencia analítica como una cobertura empírica cercana al objetivo nominal del 80 %, sin afirmar una calibración estadística definitiva.
   - Se diferencia explícitamente el modelo seleccionado por validación de su desempeño observado en test (por ejemplo, Random Forest fue seleccionado en validación para Zone 3 a 7 días, pero en la evaluación final de test no sostuvo la mejora frente a la baseline estacional, como documenta el notebook).
3. **Probabilidad de pico del horizonte completo:**
   - La probabilidad reportada en la tarjeta KPI principal y en la tabla comparativa representa $P(\text{al menos una superación del P95 en el horizonte } H) = P(\max_{t \in H} Y_t \ge \text{P95}_t)$.
   - Se estima mediante 1.000 simulaciones reproducibles usando block bootstrap sincronizado de residuos multivariados de las tres zonas sobre los errores de validación, sumados a la trayectoria puntual del pronóstico:
     - Tamaño de bloque: $H$ pasos (24 horas para horizonte diario; 168 horas para horizonte semanal).
     - Muestreo sincronizado: Para cada simulación $b \in \{1..1000\}$, se extrae un único índice temporal en la serie de validación para las tres zonas simultáneamente, preservando la covarianza espacial e interdependencia de red.
     - Estructura de anticipación: Al extraer un bloque continuo de longitud $H$, se conserva la secuencia temporal y la dependencia en los bins de anticipación.
     - Limitación muestral: Las probabilidades semanales superiores al 98 % son resultados experimentales basados en los cuatro únicos orígenes semanales evaluados en diciembre de 2017.
   - El umbral P95 se mantiene fijo a partir de la información de los 14 días previos disponible exactamente en cada origen de pronóstico.
   - Prohibido reutilizar la probabilidad marginal del clasificador logístico a 1 hora como probabilidad del horizonte completo de 24h o 7 días.
   - Se incorpora al modelo semántico la tabla dedicada `Fact_Probabilidad_Pico`.
4. **Mapa de Tétouan y delimitación de redes:**
   - La v1 incluye un mapa satelital de contexto de Tétouan con los selectores de las tres subestaciones (Quads, Smir, Boussafou).
   - Prohibido inventar límites poligonales o asignar arbitrariamente barrios administrativos a las redes de distribución.
   - El sombreado coroplético de zonas queda condicionado a la obtención futura de geometrías GIS verificadas de la distribuidora.
5. **Contexto meteorológico:**
   - La información meteorológica (temperatura, humedad, velocidad del viento) refleja las observaciones históricas coincidentes y se titula "Condiciones meteorológicas observadas (Tétouan)". No se presenta como pronóstico meteorológico futuro exento de error. La integración con APIs climáticas operativas (ej. Open-Meteo) queda como desarrollo futuro.
6. **Unidades físicas:**
   - Se mantiene la denominación neutra de "unidades" o formato con miles "mil", sin conversión a kW o kWh hasta corroborar documentalmente la semántica física de la medición de UCI.
   - El umbral P95 es estadístico (ventana móvil previa de 14 días); no denota capacidad máxima ni sobrecarga física de la red.

## Narrative
- Core story: Evaluación del comportamiento y previsibilidad de la carga eléctrica en las tres redes de distribución de Tétouan durante diciembre de 2017: contraste entre la demanda observada y el pronóstico a 24 horas y 7 días con bandas de incertidumbre al 80%, y cuantificación rigurosa de la probabilidad de experimentar picos que superen el percentil 95 histórico.
- Audience promise: Proporcionar a analistas y operadores una visión consolidada del volumen medio proyectado, la magnitud y hora del pico, la incertidumbre esperada y las alertas preventivas por zona.
- Key questions answered:
  1. ¿Cuál es la demanda media y el pico máximo previsto para las próximas 24 horas o 7 días bajo el modelo seleccionado?
  2. ¿Cuál es la probabilidad simulada de que la demanda supere el umbral P95 en al menos una ocasión durante el horizonte completo?
  3. ¿Cuál es el margen de incertidumbre del pronóstico (intervalo empírico del 80%) para cada hora?
  4. ¿Qué horas individuales presentan alertas de demanda elevada según el clasificador logístico a 1 hora?
  5. ¿Cómo se comparan las tres redes (Quads, Smir, Boussafou) en demanda media, picos y riesgo de eventos elevados?

## Design identity
- Tone: Operational Command Center (alta precisión técnica, sobriedad analítica, jerarquía informativa visualmente equilibrada y densa pero limpia).
- Signature: Franja superior de perspectiva contextual e indicadores KPI combinada con una línea de pronóstico continua con banda empírica del 80%, línea de umbral P95 y panel inferior de triaje de alertas.

## Page plan
1. Demanda Eléctrica de Tétouan (Prototipo Histórico 2017)
   - Archetype: Operational Monitor / Analytical Canvas
   - Layout variant: A (Panel lateral de navegación de red + Héroe central de serie temporal continua + Tarjetas KPI operativas superiores + Fila inferior tripartita de eventos, detalle y comparativa)
   - Purpose: Monitoreo histórico, evaluación de pronósticos horarios y anticipación de picos de demanda en las redes de Tétouan.
   - Visuals:
     - Header institucional con título del proyecto, indicador de prototipo histórico, fecha de corte (`30 dic 2017 · 23:00`), modelo de pronóstico activo y modelo de picos.
     - Carril lateral izquierdo de navegación con mapa de contexto de Tétouan y selector de red (Todas las zonas, Quads, Smir, Boussafou).
     - Banner narrativo dinámico con resumen contextual en lenguaje natural y badge de alerta operativa.
     - 4 Tarjetas KPI operativas superiores:
       1. Demanda media prevista (con variación vs promedio reciente)
       2. Pico estimado (con hora del pico proyectada)
       3. Horas con demanda elevada esperadas (con % del periodo)
       4. Probabilidad de pico en el horizonte ($\ge P95$, proveniente de `Fact_Probabilidad_Pico`)
     - Cuadro meteorológico de contexto (temperatura, humedad, velocidad del viento observadas).
     - Gráfico temporal principal con:
       - Demanda real histórica (`#0A2540`)
       - Demanda pronosticada (`#0284C7`)
       - Banda de incertidumbre empírica al 80% (`#E0F2FE` entre límite inferior y superior)
       - Línea de referencia del umbral P95 (`#D97706` segmentada)
       - Marcador vertical de origen de pronóstico
       - Selectores superiores para horizonte (24 horas, 7 días) y ventana histórica (24 h, 1 mes, Todo el periodo).
     - Fila inferior tripartita:
       - Panel izquierdo: Detalle del punto seleccionado (parámetros técnicos hora a hora).
       - Panel central: Próximos eventos de demanda elevada (tabla de alertas horarias con probabilidad del clasificador logístico y badges de estado).
       - Panel derecho: Comparativo por zona (resumen matricial de Quads, Smir y Boussafou con demanda media, pico y probabilidad de pico en el horizonte).
   - Slicers/interactions:
     - Slicer de Zona (Todas las zonas, Zone 1 - Quads, Zone 2 - Smir, Zone 3 - Boussafou).
     - Slicer de Horizonte (24 horas, 7 días).
     - Slicer de Ventana Histórica (24 horas, 1 mes, Todo el periodo).
     - Cross-filtering interactivo entre la tabla de eventos, el detalle del punto y el gráfico temporal.

## Design system summary
- Theme name + base palette: Fluent Technical Energy (Azul comando `#0A2540`, Azul primario `#0052CC`, Cian pronóstico `#0284C7`, Ámbar alerta `#D97706`, Rojo pico `#DC2626`, Verde normal `#059669`, Fondo lienzo `#F4F6F9`, Superficie tarjetas `#FFFFFF`).
- Color semantics:
  - Demanda real observada: Azul oscuro / pizarra (`#0A2540`)
  - Demanda pronosticada: Azul primario (`#0284C7`)
  - Banda predictiva empírica 80%: Azul tint transparente (`#BAE6FD` / `#E0F2FE`)
  - Umbral estadístico P95: Naranja punteado (`#D97706`)
  - Evento de alta demanda / pico: Rojo carmesí (`#DC2626`)
- Typography pairing: Segoe UI Semibold (encabezados y números de impacto) + Segoe UI Regular / Tabular (tablas, subtítulos y texto analítico).
- Layout pattern: Grid 12 columnas x 12 filas, margen 20 px, medianil 16 px, lienzo 1920 x 1080 FHD.
- Accessibility commitments: Ratios de contraste superiores a 4.5:1 (texto `#0A2540` sobre fondos `#FFFFFF` y `#F4F6F9`), doble codificación en badges de estado (texto explícito + color), diferenciación de curvas por textura y grosor.

## Semantic model structure & tables

### 1. Tablas dimensionales
- **`Dim_Zona`**:
  - `zona_id` (texto, clave primaria: `zone_1_load`, `zone_2_load`, `zone_3_load`)
  - `zona_nombre` (texto: `Zone 1 - Quads`, `Zone 2 - Smir`, `Zone 3 - Boussafou`)
  - `zona_alias` (texto: `Quads`, `Smir`, `Boussafou`)
  - `orden` (entero: 1, 2, 3)
- **`Dim_Calendario`**:
  - `datetime` (fecha/hora, clave primaria a nivel horario: `2017-01-01 00:00:00` a `2017-12-30 23:00:00`)
  - `fecha` (fecha)
  - `hora` (entero: 0 a 23)
  - `hora_str` (texto: "00:00", "01:00", etc.)
  - `dia_semana` (entero: 1 a 7)
  - `dia_nombre` (texto: "Lunes", "Martes", etc.)
  - `mes_nombre` (texto: "Enero", "Febrero", etc.)
  - `es_fin_semana` (booleano)
- **`Dim_Horizonte`**:
  - `horizonte` (texto, clave primaria: `24 horas`, `7 días`)
  - `horas_horizonte` (entero: 24, 168)
  - `orden` (entero: 1, 2)
- **`Dim_Ventana_Historica`**:
  - `ventana_id` (texto: `24h`, `1mes`, `todo`)
  - `ventana_nombre` (texto: `24 horas`, `1 mes`, `Todo el periodo`)
  - `horas_atras` (entero: 24, 720, 8760)
  - `orden` (entero: 1, 2, 3)
- **`Dim_Fecha_Origen`**:
  - `fecha_origen` (fecha/hora, clave primaria: marcas de tiempo de corte evaluadas)
  - `fecha` (fecha)
  - `hora` (entero: 0 a 23)
  - `hora_str` (texto: "23:00")
  - `etiqueta_origen` (texto: e.g. "02 dic 2017 · 23:00")
  - `dia_semana` (entero: 1 a 7)
  - `dia_nombre` (texto: "Lunes", "Martes", etc.)
  - `mes_nombre` (texto: "Diciembre")
  - `orden` (entero: 1 a 28)

### 2. Tablas de hechos
- **`Fact_Demanda_Horaria`** (serie horaria observada 2017):
  - `datetime` (fecha/hora, FK a `Dim_Calendario`)
  - `zona_id` (texto, FK a `Dim_Zona`)
  - `demanda` (decimal)
  - `temperatura` (decimal)
  - `humedad` (decimal)
  - `viento` (decimal)
- **`Fact_Pronostico`** (predicciones y bandas empíricas del 80%):
  - `fecha_origen` (fecha/hora, momento de corte de emisión del pronóstico)
  - `lead_horas` (entero, horas de anticipación: 1 a 24 o 1 a 168)
  - `datetime` (fecha/hora, fecha objetivo = `fecha_origen + lead_horas`, FK a `Dim_Calendario`)
  - `zona_id` (texto, FK a `Dim_Zona`)
  - `horizonte` (texto, FK a `Dim_Horizonte`)
  - `modelo` (texto: `HistGradientBoosting`, `Estacional`, `Random Forest`)
  - `es_modelo_seleccionado` (booleano: TRUE para el modelo seleccionado en validación para esa zona y horizonte, FALSE en caso contrario)
  - `real` (decimal, valor observado real)
  - `predicho` (decimal, pronóstico puntual $\hat{y}$)
  - `predicho_inf_80` (decimal, $\hat{y} + q_{0.10}(e)$ calibrado en validación)
  - `predicho_sup_80` (decimal, $\hat{y} + q_{0.90}(e)$ calibrado en validación)
  - `threshold_p95` (decimal, umbral estadístico P95 de los 14 días previos fijado en `fecha_origen`)
- **`Fact_Probabilidad_Pico`** (probabilidad conjunta estimada para el horizonte):
  - `fecha_origen` (fecha/hora)
  - `zona_id` (texto, FK a `Dim_Zona`)
  - `horizonte` (texto, FK a `Dim_Horizonte`)
  - `modelo` (texto)
  - `probabilidad_al_menos_un_pico` (decimal, porcentaje entre 0 y 1 estimado vía simulaciones de trayectorias)
  - `pico_esperado_max` (decimal)
  - `hora_pico_esperado` (texto)
  - `horas_elevadas_esperadas` (entero)
  - `num_simulaciones` (entero: e.g. 1000)
- **`Fact_Eventos_Clasificacion`** (alertas horarias individuales del clasificador logístico):
  - `datetime` (fecha/hora, FK a `Dim_Calendario`)
  - `zona_id` (texto, FK a `Dim_Zona`)
  - `modelo` (texto: `Logistic Regression`)
  - `estrategia` (texto: `Seleccionado`)
  - `real` (entero: 0 o 1)
  - `probabilidad` (decimal, probabilidad horaria del modelo logístico)
  - `umbral_probabilidad` (decimal: 0.50 o 0.80 según política)
  - `threshold_p95` (decimal)
  - `prediccion` (entero: 0 o 1)
  - `estado_predicho` (texto: `Demanda elevada`, `Normal`)
  - `estado_real` (texto: `Demanda elevada`, `Normal`)

### 3. Relaciones del modelo
- `Dim_Zona[zona_id]` $1 \to *$ `Fact_Demanda_Horaria[zona_id]`
- `Dim_Zona[zona_id]` $1 \to *$ `Fact_Pronostico[zona_id]`
- `Dim_Zona[zona_id]` $1 \to *$ `Fact_Probabilidad_Pico[zona_id]`
- `Dim_Zona[zona_id]` $1 \to *$ `Fact_Eventos_Clasificacion[zona_id]`
- `Dim_Calendario[datetime]` $1 \to *$ `Fact_Demanda_Horaria[datetime]`
- `Dim_Calendario[datetime]` $1 \to *$ `Fact_Pronostico[datetime]`
- `Dim_Calendario[datetime]` $1 \to *$ `Fact_Eventos_Clasificacion[datetime]`
- `Dim_Horizonte[horizonte]` $1 \to *$ `Fact_Pronostico[horizonte]`
- `Dim_Horizonte[horizonte]` $1 \to *$ `Fact_Probabilidad_Pico[horizonte]`
- `Dim_Fecha_Origen[fecha_origen]` $1 \to *$ `Fact_Pronostico[fecha_origen]`
- `Dim_Fecha_Origen[fecha_origen]` $1 \to *$ `Fact_Probabilidad_Pico[fecha_origen]`

### 4. Medidas DAX principales
- `Demanda Real = AVERAGE(Fact_Demanda_Horaria[demanda])`
- `Demanda Pronosticada = AVERAGE(Fact_Pronostico[predicho])`
- `Banda Superior 80% = AVERAGE(Fact_Pronostico[predicho_sup_80])`
- `Banda Inferior 80% = AVERAGE(Fact_Pronostico[predicho_inf_80])`
- `Umbral P95 = AVERAGE(Fact_Pronostico[threshold_p95])`
- `Demanda Media Prevista = AVERAGE(Fact_Pronostico[predicho])`
- `Pico Estimado = MAXX(Fact_Pronostico, Fact_Pronostico[predicho])`
- `Hora Pico Estimado = CALCULATE(SELECTEDVALUE(Dim_Calendario[hora_str]), FILTER(Fact_Pronostico, Fact_Pronostico[predicho] = [Pico Estimado]))`
- `Horas Demanda Elevada = COUNTROWS(FILTER(Fact_Pronostico, Fact_Pronostico[predicho] >= Fact_Pronostico[threshold_p95]))`
- `Pct Horas Elevadas = DIVIDE([Horas Demanda Elevada], COUNTROWS(Fact_Pronostico))`
- `Probabilidad Pico Horizonte = AVERAGE(Fact_Probabilidad_Pico[probabilidad_al_menos_un_pico])`
- `Resumen Perspectiva Dinamica = "Se proyecta una demanda media de " & FORMAT([Demanda Media Prevista], "#,##0") & " unidades, con un pico estimado de " & FORMAT([Pico Estimado], "#,##0") & " alrededor de las " & [Hora Pico Estimado] & ". Se esperan " & [Horas Demanda Elevada] & " horas con demanda elevada (por encima del P95)."`
- `Alerta Estado Operativo = IF([Probabilidad Pico Horizonte] >= 0.50 || [Horas Demanda Elevada] > 0, "Se anticipan picos de demanda en el horizonte seleccionado.", "Comportamiento dentro de los rangos normales esperados.")`

## Canonical design contract

```yaml
Design Brief:
  generated_by: powerbi-report-cli
  contract_version: 1
  mode: greenfield
  design_identity:
    tone: "Operational Command Center"
    signature: "Top narrative alert banner with multi-metric KPI tiles, continuous dual-stream forecast timeline with 80% empirical quantile uncertainty envelope, P95 reference threshold, and simulated horizon peak probability"
  archetype: "Operational Monitor"
  navigation_model: "none"
  color_map:
    - measure: "Fact_Demanda_Horaria[Demanda Real]"
      color: "#0A2540"
      tint: "#E2E8F0"
    - measure: "Fact_Pronostico[Demanda Pronosticada]"
      color: "#0284C7"
      tint: "#E0F2FE"
    - measure: "Fact_Pronostico[Umbral P95]"
      color: "#D97706"
      tint: "#FEF3C7"
    - measure: "Fact_Probabilidad_Pico[Probabilidad Pico Horizonte]"
      color: "#DC2626"
      tint: "#FEE2E2"
  pages:
    - name: "Demanda Eléctrica de Tétouan"
      role: "landing"
      archetype: "Operational"
      layout_variant: "A"
      variant_rationale: "Optimized for continuous historical load monitoring and peak alert response with left zone selector rail, top operational perspective, central dual-stream forecast timeline, and bottom triage detail row."
      page_background: "#F4F6F9"
      layout_summary: "Header with 2017 historical prototype status, left rail with geographic zone selector, top operational narrative and 4-KPI strip, central historical-forecast timeline with 80% empirical envelope, and bottom tripartite event and comparison grid."
      layout_contract:
        canvas:
          width: 1920
          height: 1080
          margin: 20
          gutter: 16
          snap: 8
        grid:
          columns: 12
          rows: 12
          regions:
            header:        [1,  1, 13,  2]
            left_rail:     [1,  2,  3, 13]
            top_narrative: [3,  2, 11,  3]
            weather_box:   [11, 2, 13,  4]
            kpi_strip:     [3,  3, 11,  5]
            hero_trend:    [3,  5, 13,  9]
            detail_left:   [3,  9,  6, 13]
            detail_mid:    [6,  9, 10, 13]
            detail_right:  [10, 9, 13, 13]
        placements:
          - id: page_title
            region: header
            kind: textbox
            text: "Demanda Eléctrica de Tétouan | Pronóstico de demanda y detección de picos (Prototipo Histórico 2017)"
            purpose: "Header banner with project identity, model metadata, and 2017 historical cut-off timestamp."
          - id: zone_selector_rail
            region: left_rail
            kind: slicer
            field_bindings: Dim_Zona[zona_nombre]
            slicer_type: tile
            purpose: "Single-select or multi-select distribution network zone filtering (Todas las zonas, Quads, Smir, Boussafou)."
          - id: narrative_summary
            region: top_narrative
            kind: textbox
            field_bindings: [Measures[Resumen Perspectiva Dinamica], Measures[Alerta Estado Operativo]]
            purpose: "Dynamic natural-language overview for the upcoming 24 hours / 7 days with conditional alert badge."
          - id: weather_widget
            region: weather_box
            kind: cardVisual
            field_bindings: [Fact_Demanda_Horaria[temperatura], Fact_Demanda_Horaria[humedad], Fact_Demanda_Horaria[viento]]
            purpose: "Observed historical weather context panel for temperature, humidity and wind speed."
          - id: kpi_avg_demand
            region: kpi_strip
            kind: cardVisual
            field_bindings: Measures[Demanda Media Prevista]
            slot: 1
            of: 4
            purpose: "Average forecasted power demand for the selected horizon."
          - id: kpi_peak_demand
            region: kpi_strip
            kind: cardVisual
            field_bindings: Measures[Pico Estimado]
            slot: 2
            of: 4
            purpose: "Estimated peak demand value and predicted peak hour timestamp."
          - id: kpi_high_demand_hours
            region: kpi_strip
            kind: cardVisual
            field_bindings: Measures[Horas Demanda Elevada]
            slot: 3
            of: 4
            purpose: "Total hours expected to exceed the 95th percentile threshold."
          - id: kpi_peak_probability
            region: kpi_strip
            kind: cardVisual
            field_bindings: Measures[Probabilidad Pico Horizonte]
            slot: 4
            of: 4
            purpose: "Simulated joint probability of at least one peak event exceeding P95 during the selected horizon."
          - id: main_demand_forecast_chart
            region: hero_trend
            kind: lineChart
            field_bindings:
              X: Dim_Calendario[datetime]
              Y:
                - Measures[Demanda Real]
                - Measures[Demanda Pronosticada]
                - Measures[Banda Inferior 80%]
                - Measures[Banda Superior 80%]
                - Measures[Umbral P95]
            sort_policy: value_asc
            color_strategy: measure_match
            purpose: "Central timeline displaying historical observations, forecast, 80% empirical quantile prediction envelope, and P95 threshold."
          - id: selected_point_detail
            region: detail_left
            kind: tableEx
            field_bindings:
              - Dim_Calendario[datetime]
              - Measures[Demanda Pronosticada]
              - Measures[Umbral P95]
              - Fact_Eventos_Clasificacion[probabilidad]
            purpose: "Focused technical readout for the user-selected point or active hour."
          - id: upcoming_high_demand_events
            region: detail_mid
            kind: tableEx
            field_bindings:
              - Fact_Eventos_Clasificacion[datetime]
              - Dim_Zona[zona_alias]
              - Fact_Pronostico[predicho]
              - Fact_Eventos_Clasificacion[probabilidad]
              - Fact_Eventos_Clasificacion[estado_predicho]
            sort_policy: value_desc
            color_strategy: semantic
            purpose: "Triage log of forthcoming high-demand events with hourly classification probability ratings and status badges."
          - id: zone_comparison_table
            region: detail_right
            kind: tableEx
            field_bindings:
              - Dim_Zona[zona_alias]
              - Measures[Demanda Media Prevista]
              - Measures[Pico Estimado]
              - Measures[Probabilidad Pico Horizonte]
            purpose: "Side-by-side performance summary comparing Quads, Smir, and Boussafou."
        space_audit:
          content_cell_count: 144
          placed_cell_count: 144
          empty_cell_pct: 0
          unplaced_regions: []
          largest_region:
            name: hero_trend
            pct_of_content: 33.3
          balance_rationale: "Dominant central timeline occupies one-third of the canvas; the operational narrative and KPI strip occupy the upper third; the structured triage detail row occupies the bottom third; the left rail cleanly isolates distribution network navigation."
  interaction_pattern:
    drill_targets: []
    cross_filter_rules:
      - source: zone_selector_rail
        target: "*"
        action: Filter
      - source: upcoming_high_demand_events
        target: main_demand_forecast_chart
        action: Highlight
      - source: main_demand_forecast_chart
        target: selected_point_detail
        action: Filter
  accessibility:
    alt_text_strategy: "headline+trend"
    contrast_notes: "Deep slate text #0A2540 on #FFFFFF and #F4F6F9 surfaces exceeds 7:1 ratio. Alert indicators use distinct shapes and double-coding (text badge + color) to support color-blind users."
  theme:
    base: "fluent2"
    user_overrides: "Preserve crisp energy intelligence styling, high contrast tabular numerals, and subtle border-radius cards."
```

## Implementation notes
- Model changes: Desarrollar un script modular y reproducible en Python (`src/python/export_powerbi_tables.py`) que:
  1. Extraiga los errores de validación de cada modelo/zona/horizonte.
  2. Calcule los cuantiles empíricos $q_{0.10}$ y $q_{0.90}$ agrupados por bins de `lead_horas`.
  3. Ejecute simulaciones de trayectorias (1.000 iteraciones vía remuestreo conjunto de residuos) para calcular la probabilidad de al menos un pico en el horizonte.
  4. Audite cobertura y amplitud en test sin usar test para calibrar.
  5. Genere las tablas dimensionales y de hechos en `outputs/powerbi/`.
  6. Escriba las definiciones TMDL en `powerbi/Energy_Demand_Intelligence.SemanticModel/definition/tables/` y relaciones.
- PBIR/report authoring: Actualizar la definición del reporte en `powerbi/Energy_Demand_Intelligence.Report/definition/pages/fee72c677b8c7615b78a/page.json` y `visuals/` con el layout exacto especificado.
- Validation: Validar sintaxis y referencias con `powerbi-report-author validate`.
- Desktop screenshot verification: Abrir el archivo `.pbip` en Power BI Desktop para comprobación visual, interacción y captura de pantalla.
- Publishing boundary: Local únicamente.
- Risks & limitations:
  - Serie limitada a 2017 (finaliza el 30 de diciembre a las 23:50; documentado).
  - Geometrías GIS ausentes en fuente original; mapa v1 opera a nivel contextual/topológico.
  - La probabilidad del horizonte completo es simulada sobre trayectorias multivariadas y difiere conceptualmente de la probabilidad horaria marginal del clasificador logístico a 1 hora.
