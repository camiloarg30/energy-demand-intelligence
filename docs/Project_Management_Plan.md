# Energy Demand Intelligence

## Plan de dirección del proyecto

**Responsable** Juan Camilo Sánchez Navarro  
**Versión** 0.1  
**Fecha** 7 de noviembre de 2026

## 1. Propósito

Desarrollar un prototipo reproducible para pronosticar la carga eléctrica horaria de tres zonas de Tétouan, Marruecos, y detectar periodos de demanda estadísticamente elevada. El proyecto integrará análisis temporal, modelos estadísticos, machine learning, automatización, visualización y documentación técnica.

La base disponible corresponde a 2017. Por tanto, el alcance actual es una demostración histórica. La operación con pronósticos de 2026 requiere una fuente reciente de demanda eléctrica y un proceso autorizado para acceder a ella.

## 2. Objetivos del proyecto

1. Caracterizar los registros de consumo y las variables meteorológicas disponibles.
2. Construir pronósticos horarios por zona para horizontes de 24 horas y siete días.
3. Comparar referencias ingenuas, AutoARIMA y modelos de regresión con machine learning.
4. Desarrollar una clasificación separada para identificar demanda estadísticamente elevada.
5. Evaluar los modelos con validación temporal y métricas adecuadas a cada problema.
6. Automatizar la generación de resultados y presentarlos en Power BI.
7. Documentar una arquitectura AWS viable y desplegarla cuando se disponga de las cuentas, permisos y fuentes necesarias.
8. Mantener código, resultados y decisiones versionados en GitHub.

## 3. Alcance

### Incluido

- Tres zonas de consumo disponibles en el dataset de Tétouan.
- Granularidad horaria candidata y horizontes de 24 y 168 horas, sujetos a confirmación de la semántica física de la variable.
- Modelos de referencia naive y seasonal naive.
- AutoARIMA con selección automática de órdenes mediante `forecast::auto.arima()` en R.
- Modelos de regresión con machine learning cuando aporten valor frente a las referencias.
- Clasificación de demanda estadísticamente elevada, con umbrales definidos usando exclusivamente datos de entrenamiento.
- Evaluación cronológica, análisis de errores y diagnósticos de residuos.
- Un notebook maestro con las seis fases de CRISP-DM.
- Scripts reutilizables en Python y R, pipeline local, dashboard Power BI y documentación del despliegue.

### Excluido

- Afirmar sobrecarga, riesgo de red o insuficiencia de capacidad sin límites técnicos y mediciones de infraestructura.
- Atribuir ahorros, costos evitados o beneficios financieros sin datos económicos.
- Presentar datos meteorológicos observados después del origen como variables conocidas al pronosticar.
- Presentar el dataset de 2017 como demanda actual.
- Desplegar un servicio operacional antes de contar con una fuente de demanda actual, permisos y pruebas de operación.

## 4. Criterios de aceptación

| ID | Criterio | Evidencia requerida |
|---|---|---|
| AC01 | El análisis se reproduce desde un entorno limpio. | Instrucciones, dependencias fijadas y ejecución completa del notebook. |
| AC02 | La fuente y las transformaciones quedan trazables. | Diccionario, auditoría, reglas de preparación y referencia UCI. |
| AC03 | Las comparaciones de forecasting usan los mismos orígenes y horizontes. | Tabla de backtesting por zona, horizonte y modelo. |
| AC04 | AutoARIMA selecciona los órdenes automáticamente. | Script R, argumentos registrados, versión del paquete y modelo seleccionado. |
| AC05 | No existe fuga de información temporal. | Diseño de origen móvil y documentación de variables disponibles al origen. |
| AC06 | La clasificación usa un umbral calculado solo con entrenamiento. | Código reproducible y métricas de clasificación por zona. |
| AC07 | Power BI responde preguntas de uso concretas. | Reporte con pronóstico, incertidumbre, alertas y calidad histórica. |
| AC08 | El repositorio puede ser comprendido y reproducido por otra persona. | README, estructura, licencia definida, instrucciones y commits. |
| AC09 | Las limitaciones se comunican con claridad. | Nota visible sobre 2017, unidades no confirmadas y alcance histórico. |
| AC10 | AWS ejecuta un flujo verificable y controlado. | Diagrama, logs, control de errores, costos y prueba de actualización. |

## 5. Dirección del proyecto según PMI

Se utilizarán los cinco grupos de procesos como marco de gestión. No se tratarán como etapas rígidas que ocurren una sola vez.

| Grupo | Aplicación en el proyecto | Producto de gestión |
|---|---|---|
| Inicio | Acordar problema, propósito, alcance inicial y criterios de éxito. | Project charter. |
| Planificación | Descomponer trabajo, definir cronograma, dependencias, calidad, riesgos, recursos y comunicaciones. | Este plan y la EDT. |
| Ejecución | Desarrollar datos, modelos, pipeline, Power BI y AWS. | Entregables técnicos. |
| Seguimiento y control | Revisar avance, calidad, riesgos, cambios y cumplimiento de criterios. | Registro de decisiones, riesgos y estado. |
| Cierre | Aceptar entregables, documentar resultados, publicar el repositorio y registrar lecciones. | Informe final y cierre. |

La referencia de dirección será la PMBOK Guide, octava edición, adaptada al tamaño y al carácter demostrativo del proyecto. Se priorizarán gobierno, alcance, cronograma, finanzas, interesados, recursos y riesgos. No se adoptará burocracia que no contribuya al control real.

## 6. Desarrollo analítico con CRISP-DM

| Fase | Actividades principales | Condición de salida |
|---|---|---|
| Business Understanding | Contexto, usuario, decisiones, objetivos analíticos, restricciones y éxito. | Pregunta de negocio y criterios aprobados. |
| Data Understanding | Fuente, diccionario, cobertura, integridad, exploración, calidad e insights. | Hallazgos y limitaciones documentados. |
| Data Preparation | Selección, limpieza, agregación, features, particiones y trazabilidad. | Dataset de modelado reproducible. |
| Modeling | Baselines, AutoARIMA, regresión ML y clasificación. | Candidatos entrenados con configuración registrada. |
| Evaluation | Backtesting, comparación, errores, residuos, incertidumbre y alertas. | Decisión de selección respaldada por evidencia. |
| Deployment | Pipeline, salidas, Power BI, AWS, monitoreo y mantenimiento. | Ejecución repetible y entrega validada. |

Las fases pueden iterarse si un resultado obliga a revisar una decisión anterior.

### 6.1. Estructura de desglose del trabajo

| WBS | Paquete de trabajo | Dependencia | Entregable |
|---|---|---|---|
| 1.0 | Dirección y gobierno | Ninguna | Charter, plan, riesgos y decisiones. |
| 1.1 | Alcance y criterios de aceptación | 1.0 | Alcance y Definition of Done. |
| 1.2 | Cronograma y riesgos | 1.1 | Hitos, dependencias y registro de riesgos. |
| 2.0 | Entorno de desarrollo | 1.0 | VS Code, Python, R y Git verificados. |
| 2.1 | Repositorio y reglas de trabajo | 2.0 | GitHub, README y AGENTS.md. |
| 3.0 | Base analítica | 2.0 | Datos auditados y preparación reproducible. |
| 3.1 | Resolución temporal y semántica | 3.0 | Unidad de análisis documentada o limitación explícita. |
| 3.2 | Particiones y features | 3.1 | Protocolo temporal sin fuga. |
| 4.0 | Pronóstico | 3.2 | Baselines, AutoARIMA y candidatos ML. |
| 4.1 | Evaluación de forecasting | 4.0 | Backtesting por zona y horizonte. |
| 5.0 | Clasificación de demanda elevada | 3.2 | Etiqueta, umbral y clasificador evaluado. |
| 6.0 | Pipeline local | 4.1 y 5.0 | Ejecución reproducible y salidas estructuradas. |
| 7.0 | Power BI | 6.0 | Dashboard funcional y validado. |
| 8.0 | AWS | 6.0 y 7.0 | Despliegue y monitoreo, condicionado a fuentes y permisos. |
| 9.0 | Cierre y portafolio | 7.0 y 8.0 o decisión documentada de no desplegar | README, brief final, evidencia y lecciones. |

### 6.2. Hitos de control

| Hito | Condición de aceptación |
|---|---|
| H1. Plan aprobado | Alcance, WBS, criterios y riesgos registrados. |
| H2. Entorno listo | Python, R, Git y notebook funcionan desde VS Code. |
| H3. Datos preparados | Granularidad, unidades y particiones documentadas. |
| H4. Modelos comparados | Backtesting común y resultados por zona y horizonte. |
| H5. Pipeline local | Una ejecución produce las tablas de salida esperadas. |
| H6. Dashboard validado | Los indicadores coinciden con las salidas del pipeline. |
| H7. Cloud validado | La automatización se ejecuta, registra errores y controla costos. |
| H8. Cierre | Repositorio, documentación y limitaciones revisados. |

### 6.3. Cronograma y regla de avance

El orden de los paquetes establece la secuencia. La duración real se ajustará según los resultados, la instalación local y el acceso a fuentes y servicios externos. No se declarará completado un hito por haber escrito el código. Se requiere evidencia de ejecución y cumplimiento de sus criterios de aceptación.

## 7. Protocolo estadístico y de machine learning

### 7.1. Pronóstico de carga

Se evaluarán por zona y horizonte los siguientes candidatos.

1. Naive de persistencia.
2. Naive estacional diario y semanal.
3. AutoARIMA mediante `forecast::auto.arima()` en R.
4. Regresión con machine learning en Python, con variables disponibles al origen del pronóstico.
5. Extensión con regresores externos solo cuando se disponga de esos valores en el momento de emitir el pronóstico.

AutoARIMA realizará la selección de órdenes. No se elegirán manualmente los parámetros ARIMA o SARIMA. Se registrarán criterio de información, configuración, versión del paquete, modelo seleccionado, residuos e intervalos de pronóstico.

La especificación inicial podrá usar una estacionalidad diaria de 24 observaciones para la serie horaria. El patrón semanal se estudiará con variables de calendario conocidas y evaluación temporal. La decisión final dependerá de diagnóstico y backtesting.

### 7.2. Evaluación de forecasting

- MAE como métrica principal.
- RMSE como métrica complementaria para errores grandes.
- WAPE para comparación relativa entre series y periodos.
- Cobertura de intervalos de predicción cuando el método los proporcione.
- Resultados separados por zona, horizonte y ventana temporal.

La comparación utilizará rolling forecasting origin. En cada origen, el entrenamiento contendrá solo observaciones anteriores y el pronóstico cubrirá 24 o 168 horas. Los candidatos se medirán sobre las mismas fechas.

El periodo de prueba de diciembre de 2017 ya fue inspeccionado en una comparación anterior. Se conservará como resultado histórico documentado, pero no se presentará como un holdout intacto para nuevas selecciones. La comparación nueva de AutoARIMA deberá usar un protocolo rolling-origin común y reportar esta limitación.

### 7.3. Clasificación de demanda elevada

La etiqueta indicará si la carga observada supera un umbral estadístico por zona. Como primera referencia se estudiará el percentil 95 de cada zona, calculado únicamente con el conjunto de entrenamiento de cada partición. Se evaluarán precision, recall, F1, PR-AUC y tasa de falsas alarmas.

El umbral identifica observaciones altas respecto al histórico. No equivale a una alarma de sobrecarga ni a un límite técnico de la red.

### 7.4. Variables meteorológicas

La meteorología observada durante el horizonte futuro no podrá usarse como si se conociera al emitir el pronóstico. Su aporte se probará mediante información meteorológica disponible en el origen, pronósticos archivados o un análisis retrospectivo identificado explícitamente como tal.

## 8. Entorno tecnológico

| Componente | Decisión inicial | Propósito |
|---|---|---|
| Editor | Visual Studio Code | Entorno principal de desarrollo. |
| Asistente | Google Antigravity | Apoyo para inspección y cambios revisables. |
| Python | Entorno virtual `.venv` | Preparación, ML, clasificación y orquestación. |
| R | Script independiente | AutoARIMA con paquete `forecast`. |
| Notebook | Un único `.ipynb` maestro con kernel Python | Narrativa CRISP-DM y coordinación del análisis. |
| Git | Local | Historial y ramas. |
| GitHub | Repositorio público de portafolio, una vez revisado | Código, documentación y colaboración mediante Pull Requests. |
| Power BI | Archivo `.pbix` y datos de salida | Visualización y análisis de resultados. |
| AWS | S3, EventBridge Scheduler, Lambda o contenedor y CloudWatch. Athena solo si se justifica. | Almacenamiento, programación, ejecución, consulta y monitoreo. |

El notebook Python llamará al script R mediante `Rscript` y leerá una salida estructurada. Esta integración permite mantener un solo notebook sin introducir un kernel multilenguaje complejo. Los kernels SoS o la integración `rpy2` son alternativas posibles, pero no son necesarias para este alcance.

### 8.1. Power BI y diseño visual

La primera versión utilizará visuales nativos, medidas DAX, temas y tooltips. HTML y CSS se considerarán solo para componentes concretos. Power BI permite desarrollar visuales propios empaquetados como `.pbiviz`, pero eso requiere TypeScript y el entorno de desarrollo de visuales. También existen visuales de AppSource que representan HTML, sujetos al sandbox y sus limitaciones. No se construirá el dashboard principal sobre HTML embebido.

Los visuales de Python y R tampoco serán el mecanismo central de interacción. Se utilizarán como máximo para análisis complementarios cuando sus límites de servicio, filas, tiempo de ejecución e interacción sean aceptables.

Referencias técnicas  
- https://learn.microsoft.com/en-us/power-bi/developer/visuals/develop-power-bi-visuals  
- https://learn.microsoft.com/en-us/power-bi/visuals/service-r-visuals  
- https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-python-visuals

## 9. Estructura del repositorio

```text
energy-demand-intelligence/
├── AGENTS.md
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── Energy_Demand_Intelligence.ipynb
├── src/
│   ├── python/
│   └── r/
├── outputs/
│   ├── forecasts/
│   └── powerbi/
├── reports/
│   ├── figures/
│   └── tables/
├── powerbi/
├── docs/
│   ├── Project_Management_Plan.md
│   ├── Antigravity_Prompts.md
│   ├── CRISP_DM_and_Notebooks.md
│   └── Energy_Demand_Intelligence_Brief.pdf
└── .github/
    └── pull_request_template.md
```

Los archivos generados de gran tamaño, credenciales, entornos locales y resultados transitorios no se versionarán. Los datos originales se conservarán sin modificación y con la referencia de UCI.

## 10. Trabajo de hoy

La meta de la sesión es terminar un prototipo histórico local reproducible y presentable. El despliegue operativo con demanda actual queda condicionado a resolver la fuente de datos reciente.

| Orden | Actividad | Salida verificable |
|---|---|---|
| 1 | Instalar y comprobar VS Code, Python, Git y R. | Versiones disponibles desde la terminal. |
| 2 | Abrir el repositorio y crear `.venv`. | Kernel Python del proyecto seleccionado. |
| 3 | Ejecutar el notebook desde cero. | Todas las celdas ejecutadas sin errores. |
| 4 | Implementar AutoARIMA en R y su integración con Python. | Pronósticos por zona y horizonte guardados en CSV. |
| 5 | Definir y evaluar la clasificación de demanda elevada. | Etiquetas, probabilidades y métricas con umbral sin fuga. |
| 6 | Construir el pipeline local. | Una ejecución genera las tablas requeridas por Power BI. |
| 7 | Preparar el dashboard. | Páginas funcionales con datos históricos y pronósticos experimentales. |
| 8 | Crear el repositorio GitHub y publicar la primera versión revisada. | README, historial y archivos versionados. |
| 9 | Dejar AWS documentado y desplegar solo si hay cuenta, permisos y tiempo de validación. | Arquitectura y lista de requisitos, o prueba cloud verificable. |

## 11. Costos y control financiero

No se asumirá un costo cloud antes de definir la arquitectura y estimar el volumen de ejecuciones. El primer prototipo se desarrollará localmente. Antes de crear recursos AWS se realizará una estimación en AWS Pricing Calculator, se configurará un presupuesto y alertas de gasto, se limitarán permisos y se documentará cómo apagar o eliminar recursos. El uso de servicios administrados se justificará por la necesidad de operación y no solo por demostrar tecnología.

## 12. Riesgos principales

| Riesgo | Impacto | Respuesta |
|---|---|---|
| No se confirman las unidades físicas. | Interpretación incorrecta de la carga. | Mantener la escala nativa y no etiquetar unidades. |
| Solo existe histórico de 2017. | No se demuestra desempeño actual. | Etiquetar el resultado como prototipo histórico y buscar datos recientes. |
| Se reutiliza un test ya inspeccionado. | Sesgo de selección. | Usar rolling-origin común y documentar la exposición de diciembre. |
| Fuga de información meteorológica. | Métricas artificialmente optimistas. | Usar solo regresores disponibles en cada origen. |
| AutoARIMA no supera baselines. | Complejidad sin beneficio. | Reportar la evidencia y seleccionar por desempeño real. |
| Umbral de demanda se confunde con capacidad de red. | Interpretación operativa peligrosa. | Presentarlo como señal estadística, no como sobrecarga. |
| Dependencias locales incompatibles. | Dificultad para reproducir. | Fijar versiones, aislar entornos y probar desde kernel limpio. |
| El agente modifica archivos o publica cambios sin revisión. | Pérdida de control. | Reglas persistentes, diffs revisados y aprobación humana para push o deploy. |
| La fuente de demanda no se actualiza. | No hay pronóstico operativo diario. | No automatizar como servicio real hasta resolver la fuente. |

## 13. Control del proyecto

Se mantendrán cuatro registros sencillos.

- Decisiones. Fecha, decisión, motivo y efecto sobre el alcance o diseño.
- Riesgos. Probabilidad, impacto, respuesta y estado.
- Cambios. Solicitud, justificación, impacto y aprobación.
- Hitos. Entregable, criterio de aceptación, estado y evidencia.

Cada bloque de trabajo se cierra con una comprobación reproducible. El estado de GitHub y el estado de Notion deben reflejar el mismo avance, sin utilizar Notion como sustituto del historial de código.

## 14. Cierre y publicación

El proyecto se considera terminado cuando el notebook y el pipeline se ejecuten de forma reproducible, las comparaciones estén documentadas, el dashboard responda a las preguntas definidas, el repositorio sea comprensible y las limitaciones se presenten claramente.

La publicación de GitHub incluirá README, brief ejecutivo, plan de gestión, metodología, código, instrucciones y resultados seleccionados. Antes de publicar se revisarán datos, licencias, credenciales, rutas locales, outputs y metadatos.

## 15. Referencias base

- Project Management Institute. (2025). *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*, 8th edition. https://www.pmi.org/standards/pmbok
- Shearer, C. (2000). The CRISP-DM model: The new blueprint for data mining. *Journal of Data Warehousing*, 5(4), 13-22.
- Salam, A., & El Hibaoui, A. (2018). *Power Consumption of Tetouan City*. UCI Machine Learning Repository. https://doi.org/10.24432/C5B034
- Hyndman, R. J., & Athanasopoulos, G. *Forecasting: Principles and Practice*. https://otexts.com/fpp3/
- Hyndman, R. J., & Khandakar, Y. (2008). Automatic time series forecasting: The forecast package for R. *Journal of Statistical Software*, 27(3). https://doi.org/10.18637/jss.v027.i03
