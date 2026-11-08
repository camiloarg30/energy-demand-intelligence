# 1. Configuración
library(forecast)

data_path <- "data/processed/Tetouan_Clean_v1.csv"
output_path <- "outputs/forecasts"

zones <- c("zone_1_load", "zone_2_load", "zone_3_load")

# 2. Lectura y preparación de datos
data <- read.csv(
  data_path,
  check.names = FALSE,
  fileEncoding = "UTF-8-BOM"
)

data$datetime <- as.POSIXct(
  data$datetime,
  format = "%Y-%m-%d %H:%M:%S",
  tz = "UTC"
)

if (any(is.na(data$datetime))) {
  stop("No fue posible interpretar todas las fechas.")
}

# Agrupar los seis registros de diez minutos en una hora
hour_key <- floor(as.numeric(data$datetime) / 3600) * 3600
hour_values <- sort(unique(hour_key))

hour_counts <- table(hour_key)

if (any(hour_counts != 6)) {
  stop("Existen horas incompletas. Revisar los datos.")
}

hourly <- data.frame(
  datetime = as.POSIXct(
    hour_values,
    origin = "1970-01-01",
    tz = "UTC"
  )
)

for (zone in zones) {
  hourly[[zone]] <- vapply(
    hour_values,
    function(h) mean(data[[zone]][hour_key == h]),
    numeric(1)
  )
}

if (any(diff(hour_values) != 3600)) {
  stop("Se detectaron intervalos horarios faltantes.")
}

# 3. División temporal
last_hour <- max(hourly$datetime)

last_day <- as.POSIXct(
  format(last_hour, "%Y-%m-%d", tz = "UTC"),
  tz = "UTC"
)

test_start <- last_day - 27 * 86400
validation_start <- test_start - 28 * 86400
validation_end <- test_start - 3600

cat("Inicio de validación:", format(validation_start), "\n")
cat("Fin de validación:", format(validation_end), "\n")

# 4. Configuración de horizontes
horizons <- list(
  list(label = "24 horas", steps = 24, seasonal_period = 24),
  list(label = "7 días", steps = 168, seasonal_period = 168)
)

results <- list()

# 5. Backtesting rolling origin
for (setting in horizons) {

  h <- setting$steps
  period <- setting$seasonal_period

  target_starts <- seq(
    from = validation_start,
    to = validation_end - (h - 1) * 3600,
    by = h * 3600
  )

  for (zone in zones) {

    cat("\nZona:", zone, "| Horizonte:", setting$label, "\n")

    for (target_start in target_starts) {

      origin <- target_start - 3600
      origin_idx <- match(origin, hourly$datetime)

      if (is.na(origin_idx) || origin_idx < period * 2) {
        stop("No hay suficiente historial para ajustar el modelo.")
      }

      history <- hourly[[zone]][seq_len(origin_idx)]

      target_idx <- seq.int(origin_idx + 1, origin_idx + h)
      actual <- hourly[[zone]][target_idx]

      # Modelo AutoARIMA
      fit <- forecast::auto.arima(
  ts(history, frequency = period),
  seasonal = TRUE,
  stepwise = TRUE,
  approximation = TRUE,
  max.p = 3,
  max.q = 3,
  max.P = 1,
  max.Q = 1,
  max.order = 5,
  allowdrift = TRUE,
  allowmean = TRUE
)
      prediction <- as.numeric(
        forecast::forecast(fit, h = h)$mean
      )

      # Baselines para comparación
      persistence <- rep(tail(history, 1), h)
      seasonal <- tail(history, h)

      methods <- list(
        "Persistencia" = persistence,
        "Estacional" = seasonal,
        "AutoARIMA" = prediction
      )

      for (method in names(methods)) {

        results[[length(results) + 1]] <- data.frame(
          horizonte = setting$label,
          inicio_pronostico = target_start,
          zona = zone,
          modelo = method,
          datetime = hourly$datetime[target_idx],
          real = actual,
          predicho = methods[[method]]
        )
      }
    }
  }
}

# 6. Consolidación y métricas
predictions <- do.call(rbind, results)

groups <- split(
  predictions,
  interaction(
    predictions$horizonte,
    predictions$zona,
    predictions$modelo,
    drop = TRUE
  )
)

metrics <- do.call(rbind, lapply(groups, function(g) {

  errors <- g$real - g$predicho

  data.frame(
    horizonte = g$horizonte[1],
    zona = g$zona[1],
    modelo = g$modelo[1],
    MAE = mean(abs(errors)),
    RMSE = sqrt(mean(errors^2)),
    WAPE_pct = 100 * sum(abs(errors)) / sum(abs(g$real)),
    observaciones = nrow(g)
  )
}))

metrics <- metrics[
  order(metrics$horizonte, metrics$zona, metrics$MAE),
]

# 7. Exportación
dir.create(output_path, recursive = TRUE, showWarnings = FALSE)

write.csv(
  predictions,
  file.path(output_path, "auto_arima_validation_predictions.csv"),
  row.names = FALSE
)

write.csv(
  metrics,
  file.path(output_path, "auto_arima_validation_metrics.csv"),
  row.names = FALSE
)

cat("\nResultados de validación\n")
print(metrics, row.names = FALSE)

cat("\nArchivos exportados correctamente.\n")