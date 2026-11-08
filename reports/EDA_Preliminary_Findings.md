# Hallazgos preliminares del EDA

## Síntesis ejecutiva

El archivo local contiene 52.416 registros y nueve variables, con una frecuencia de diez minutos. La secuencia observada no presenta nulos, filas duplicadas, marcas de tiempo duplicadas ni intervalos internos distintos de diez minutos. Sin embargo, el archivo termina el 30 de diciembre de 2017 a las 23:50 y no contiene las 144 observaciones del 31 de diciembre. UCI reporta 52.417 instancias, una más que el archivo local. La diferencia queda documentada y no se imputa.

El hallazgo exploratorio prioritario es la caída de la carga media registrada de Zone 3 entre agosto y septiembre de 2017. La media mensual desciende aproximadamente de 24.648,9 a 14.922,8 en la escala original, equivalente a una variación de −39,5%. Durante el mismo periodo Zone 2 desciende 18,2% y Zone 1 desciende 8,3%. La revisión diaria muestra que la caída ocurre durante varios días, no como un único registro aislado. Además, `wind_speed` pasa de una media diaria cercana a 4,92 el 2 de septiembre a 3,82 el 3 de septiembre y 0,24 el 4 de septiembre. La coincidencia temporal puede indicar un cambio de régimen en una o más señales, pero no permite establecer una causa. La señal debe investigarse antes de fijar reglas de limpieza o entrenar modelos.

## Calidad y cobertura

| Control | Resultado | Implicación |
|---|---|---|
| Filas y columnas | 52.416 × 9 | Coincide con el CSV local auditado |
| Primera marca de tiempo | 2017-01-01 00:00 | Inicio de la cobertura observada |
| Última marca de tiempo | 2017-12-30 23:50 | No cubre el 31 de diciembre |
| Valores nulos | 0 | No se requiere imputación de celdas nulas |
| Filas duplicadas | 0 | No se detectan filas duplicadas exactas |
| Marcas de tiempo duplicadas | 0 | No se repiten timestamps |
| Intervalos internos fuera de diez minutos | 0 | La secuencia observada es regular |
| Registros esperados para todo 2017 | 52.560 | El CSV local tiene 144 registros menos |
| Instancias reportadas por UCI | 52.417 | Persiste una diferencia de una fila frente al CSV local |

La secuencia temporal es regular dentro del periodo disponible, pero la regularidad no implica cobertura anual completa. El archivo fuente se conserva intacto y los datos ausentes al cierre no se sintetizan.

## Lecturas exploratorias

- Las medias de carga son diferentes entre las tres zonas. Las primeras comparaciones de modelos deben conservar los resultados por zona.
- Los perfiles horarios, semanales y mensuales describen el comportamiento dentro del periodo observado. El archivo contiene un solo año incompleto, por lo que no permite establecer estacionalidad interanual.
- Las correlaciones entre zonas y variables ambientales son descriptivas. No demuestran causalidad ni aseguran utilidad predictiva.
- El uso operativo de meteorología debe considerar lo que realmente estaría disponible al emitir cada pronóstico. El clima observado durante el periodo objetivo no puede sustituir a un pronóstico meteorológico histórico archivado.
- UCI no documenta las unidades físicas en su tabla de variables. Parte de la literatura reporta las cargas en kW, pero la unidad permanece provisional para el CSV local.

## Decisiones de preparación

1. Mantener las tres zonas como objetivos separados durante las primeras comparaciones.
2. No eliminar observaciones de agosto o septiembre hasta investigar el cambio de nivel.
3. No convertir las variables de carga a kWh sin confirmar su semántica física.
4. Usar una serie horaria candidata para los horizontes de 24 horas y siete días. La agregación por media queda condicionada a confirmar que el valor representa un nivel de carga y no energía consumida en cada intervalo.
5. Mantener entrenamiento, validación y prueba cronológicos. El notebook reserva las últimas 28 jornadas como test y las 28 anteriores como validación.
6. Definir las líneas base y las métricas antes de evaluar modelos complejos.
7. Calcular los umbrales de demanda estadísticamente alta solo con datos de entrenamiento.

## Qué no puede concluirse

- El dataset de 2017 no proporciona mediciones actuales de demanda en 2026.
- La actualización de datos meteorológicos no actualiza la demanda eléctrica medida.
- El dataset no contiene tarifas, costos, capacidad nominal ni eventos operativos. Por tanto, no permite afirmar ahorros, costos evitados o riesgos de sobrecarga.
- La correlación entre clima y carga no basta para demostrar una relación causal.

## Artefactos generados

El notebook `notebooks/Energy_Demand_Intelligence.ipynb` genera un dataset estandarizado inicial, el diccionario de variables, la auditoría de calidad, tablas descriptivas, perfiles temporales y gráficos en `reports/`. La estandarización no se considera todavía la preparación definitiva para modelado.

## Fuentes

- Salam, A., & El Hibaoui, A. (2018). *Power Consumption of Tetouan City* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5B034
- Salam, A., & El Hibaoui, A. (2018). *Comparison of Machine Learning Algorithms for the Power Consumption Prediction: Case Study of Tetouan city*. https://doi.org/10.1109/IRSEC.2018.8703007
