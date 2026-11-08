# CRISP-DM y estándar del notebook maestro

## Decisión de estructura

Energy Demand Intelligence utilizará **un único notebook maestro** llamado `Energy_Demand_Intelligence.ipynb`. El notebook reunirá las seis fases de CRISP-DM y se irá completando de forma progresiva. La decisión responde a que las transformaciones, hallazgos y objetos de modelado se relacionan entre sí y deben contarse como un flujo continuo.

Un solo notebook no implica ejecutar código sin orden. Las celdas deben correr de arriba hacia abajo en un entorno limpio. Las variables permanecen disponibles en memoria durante la sesión, mientras que los artefactos que deban sobrevivir a una sesión o alimentar otro componente se guardan explícitamente. No se guardará cada paso intermedio ni se crearán archivos auxiliares sin un uso claro.

CRISP-DM contempla seis fases relacionadas que pueden requerir iteraciones, no una secuencia rígida. La guía visual CRISP-DM 1.0 compartida para este proyecto organiza tareas genéricas como definir objetivos de negocio, describir y verificar datos, seleccionar y limpiar datos, construir atributos, elegir técnicas y diseñar pruebas, evaluar los resultados frente a los criterios de éxito, planear el despliegue y definir monitorización y mantenimiento. Estas actividades se adaptan a las necesidades del proyecto. Referencia adicional: IBM, *IBM SPSS Modeler CRISP-DM Guide*, https://www.ibm.com/docs/en/SS3RA7_18.5.0/pdf/ModelerCRISPDM.pdf.

## Las seis fases en el proyecto

| Fase | Pregunta que resuelve | Actividades generales | Evidencia para avanzar |
|---|---|---|---|
| 1. Business Understanding | ¿Qué decisión se quiere apoyar y qué significa tener éxito? | Contexto, objetivos de negocio, criterios de éxito, restricciones, riesgos, objetivos analíticos y plan de proyecto | Pregunta de negocio y criterios de éxito definidos con límites explícitos |
| 2. Data Understanding | ¿Qué contienen los datos y qué tan confiables son? | Recolección, descripción, exploración y verificación de calidad | Cobertura, unidad de análisis, limitaciones y hallazgos iniciales documentados |
| 3. Data Preparation | ¿Cómo debe construirse el dataset analítico? | Selección, limpieza, construcción de atributos, integración y formato | Reglas reproducibles, dataset derivado y trazabilidad desde la fuente |
| 4. Modeling | ¿Qué técnica ofrece una predicción adecuada? | Selección de técnicas, diseño de prueba, parámetros, entrenamiento y evaluación técnica de modelos | Candidatos comparables bajo particiones temporales y baseline común |
| 5. Evaluation | ¿El resultado responde a la pregunta de negocio? | Alinear métricas con criterios de éxito, revisar resultados y proceso, definir siguientes pasos | Evidencia fuera de muestra, límites y decisión sobre el valor del modelo |
| 6. Deployment | ¿Cómo se genera y controla la salida útil para negocio? | Plan de despliegue, monitorización, mantenimiento, informe final y revisión del proyecto | Flujo reproducible, salidas rastreables y estrategia operativa explícita |

## Estándar visual y narrativo

### Jerarquía de títulos

- Título principal del notebook: `# **Energy Demand Intelligence**`.
- Fases CRISP-DM: encabezados de segundo nivel, por ejemplo `## **1. Business Understanding**`.
- Actividades dentro de una fase: tercer nivel con numeración, por ejemplo `### **2.1. Auditar integridad y cobertura temporal**`.
- Subactividades cuando sean útiles: cuarto nivel, por ejemplo `#### **2.3.1. Interpretación de calidad**`.
- Cada celda de título debe contener únicamente el título. El texto explicativo va en una celda Markdown posterior.

### Narrativa analítica

1. Antes de un bloque de código, explicar brevemente qué pregunta responde y qué hará el código.
2. Mantener el código tan corto como sea posible sin sacrificar claridad, trazabilidad ni reproducibilidad.
3. Después de un resultado relevante, interpretarlo: qué indica, qué no demuestra y qué decisión informa.
4. Conectar cada sección con la anterior y explicar el siguiente paso lógico. Evitar que el notebook sea una secuencia de outputs sin narrativa.
5. Usar lenguaje natural, preciso, concreto y conciso. No incluir párrafos extensos de metodología donde basta una decisión y su justificación.
6. Terminar cada fase con hallazgos, incertidumbres y la decisión que habilita la siguiente fase.

## Flujo de datos y reproducibilidad

- Ejecutar el notebook de arriba hacia abajo desde un kernel limpio para validar dependencias entre celdas.
- Mantener el archivo fuente intacto y guardar solo las salidas que tengan un uso posterior verificable.
- Persistir de manera explícita el dataset preparado, modelo o configuración final cuando otras ejecuciones los necesiten. No exportar cada DataFrame por defecto.
- Documentar reglas de limpieza, agregación, unidades, variables derivadas y particiones antes de usarlas en modelos.
- No sobrescribir silenciosamente salidas válidas ni ocultar fallas de ejecución.
- Cuando un bloque de código se vuelva estable y se necesite para una ejecución automatizada, extraer únicamente esa lógica a `src/` o al mecanismo de ejecución pertinente. El notebook seguirá siendo la referencia narrativa del análisis.

## Aplicación específica al proyecto

- El histórico local contiene datos de 2017 y no permite afirmar que el resultado describa la demanda real de 2026.
- Las unidades físicas no están completamente documentadas en UCI, por lo que no se convertirá carga en energía acumulada hasta confirmar su semántica.
- La caída de Zone 3 entre agosto y septiembre coincide en el tiempo con un cambio abrupto en `wind_speed`; no se ha identificado la causa ni se han eliminado observaciones.
- La caída de Zone 3 entre agosto y septiembre se investigará antes de decidir su tratamiento.
- La serie horaria candidata permite evaluar 24 horas y siete días como 24 y 168 pasos, respectivamente. Esta agregación sigue siendo provisional hasta confirmar la semántica física del target.
- La partición cronológica inicial deja las últimas 28 jornadas como test, las 28 anteriores como validación y el resto como entrenamiento. La selección se fija con validación y el test se evalúa una sola vez. Una vez utilizado, no debe reutilizarse para seguir ajustando candidatos.
- Las señales de demanda alta se definirán con criterios estadísticos basados solo en entrenamiento. No se presentarán como límites de seguridad de la red.
- El dashboard debe consumir una salida del pipeline reproducible; no debe depender de la ejecución manual del notebook maestro en producción.

## Qué documento debe vivir dónde

| Medio | Uso |
|---|---|
| Notion | Plan de trabajo, tareas, estado, decisiones y pendientes |
| GitHub | Notebook maestro, código, datos permitidos para redistribución, documentación versionada y salidas justificadas |
| Word o PDF | Brief ejecutivo y reportes que deban leerse sin ejecutar código |
| Notebook maestro | Análisis reproducible, narrativa, código, resultados, interpretación y decisiones |
| CSV y PNG | Únicamente salidas necesarias para reproducir análisis posteriores, revisar resultados o integrar el dashboard |

## Criterio para añadir archivos

Crear un archivo solo cuando tenga un propósito independiente y verificable. No separar notebooks por fases ni por pequeños experimentos. Un script o módulo adicional se justifica cuando una parte estable de la lógica deba ejecutarse automáticamente, reutilizarse o probarse por separado.
