# AGENTS.md — Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

## 1. Contexto y Propósito
Este repositorio contiene un proyecto de Ciencia de Datos de nivel portafolio orientado a determinar la viabilidad técnica, energética, geoespacial, climática y regulatoria para radicar Data Centers tradicionales y Campus de Inteligencia Artificial en las **24 jurisdicciones de Argentina** (23 provincias + CABA).

El sistema modela explícitamente dos perfiles de demanda diferenciados:
- **Perfil A — Campus de Entrenamiento IA (Alta Densidad):** Prioriza disponibilidad energética (SADI y potencial off-grid), eficiencia térmica (PUE / free cooling), disponibilidad hídrica y beneficios fiscales. Tolerante a latencia.
- **Perfil B — Nodos de Inferencia / Edge:** Prioriza baja latencia, cercanía a IXPs y cables submarinos, densidad de fibra troncal y capital humano IT.

## 2. Stack Tecnológico Oficial
- **Lenguaje y ETL:** Python 3.10+, Pandas, NumPy, PyArrow (formato Parquet).
- **Modelado y Estadística:** Scikit-learn (clustering, escalado), SciPy / simulaciones Monte Carlo.
- **Visualización Interactiva:** Streamlit + HTML/CSS personalizado (estética ejecutiva dark-mode) + Plotly / mapas interactivos.
- **Business Intelligence:** Power BI (consumiendo tablas planas preprocesadas desde `data/04_outputs/pbi_ready/`).
- **Entorno:** Usar exclusivamente el entorno virtual `.venv` ubicado en la raíz del proyecto.

## 3. Arquitectura de Carpetas (Contrato Obligatorio)
Respetar estrictamente esta estructura. No crear carpetas fuera de este esquema sin aprobación explícita:

    viabilidad-ia-datacenters-ar/
    ├── agents/                  # Instrucciones modulares por rol y contratos I/O
    ├── config/                  # Pesos de perfiles (JSON) y catálogo de fuentes (YAML)
    ├── data/
    │   ├── 01_raw/              # SOLO LECTURA. Datos crudos descargados. Nunca modificar.
    │   ├── 02_interim/          # Limpieza intermedia y normalización de nombres
    │   ├── 03_processed/        # Tabla maestra (24 jurisdicciones) y capas GeoJSON
    │   └── 04_outputs/          # Scores, clusters, Monte Carlo y carpeta pbi_ready/
    ├── src/
    │   ├── etl/                 # Scripts de extracción y limpieza
    │   ├── gis/                 # Procesamiento geoespacial y cálculo de PUE climático
    │   ├── modeling/            # Motor MCDA, clustering, Monte Carlo y proyecciones
    │   └── finance/             # [Reservado Fase 5] Simulador CAPEX/OPEX y RIGI
    ├── app/                     # Aplicación Streamlit y hojas de estilo CSS
    ├── bi/                      # Archivos de Power BI (.pbix) y documentación de medidas
    ├── notebooks/               # EDA y validación estadística reproducible
    └── docs/                    # Diccionario de datos, metodología y CHANGELOG.md

## 4. Reglas Innegociables de Calidad de Datos
1. **Cero datos inventados:** Nunca generar ni completar valores reales faltantes con datos sintéticos haciéndolos pasar por oficiales. Si un dato oficial no está disponible, dejarlo como `NaN`, documentarlo en `docs/data_dictionary.md` y proponer un proxy explícito para aprobación.
2. **Inmutabilidad de crudos:** Todo archivo en `data/01_raw/` es de solo lectura. Cualquier transformación debe escribirse en `02_interim/` o `03_processed/`.
3. **Estandarización de las 24 jurisdicciones:** Todas las tablas deben usar una clave estándar única (`jurisdiccion_id` según código INDEC de 2 dígitos y `jurisdiccion_nombre` normalizado) para evitar errores en cruces (`merge`).
4. **Proyección espacial única:** Toda capa geográfica (GeoJSON/coordenadas) debe trabajar en **EPSG:4326 (WGS84)**.
5. **Trazabilidad total:** Cada dataset incorporado debe registrarse en `config/data_sources.yaml` con: fuente oficial, URL, fecha de corte y periodicidad.
6. **Separación de lógica y UI:** Nunca programar cálculos del modelo de viabilidad dentro de la interfaz de Streamlit ni en fórmulas DAX complejas de Power BI. Todo cálculo vive en `src/modeling/` y se exporta versionado a `data/04_outputs/`.

## 5. Reglas Operativas y Gobernanza en Antigravity
- **Planificar antes de actuar:** Para cualquier tarea que cree o modifique más de un archivo, generar primero un Plan de Implementación (Artifact) y esperar aprobación humana.
- **Cambios atómicos:** Ejecutar un objetivo por vez. No mezclar tareas de ETL con diseño de interfaz.
- **Control de dependencias:** Antes de instalar cualquier librería nueva con `pip`, informar el motivo y actualizar `requirements.txt`.
- **Registro de decisiones:** Toda modificación estructural, cambio de peso o imputación aprobada debe registrarse en `docs/CHANGELOG.md` con fecha.
- **Protección de Git:** No ejecutar comandos destructivos de Git (`reset --hard`, `push --force`). Proponer mensajes de commit claros al finalizar cada hito validado.

## 6. Roles Lógicos del Proyecto
El agente asumirá uno de estos roles según la instrucción activa:
1. **Orquestador (PMO):** Estructura, control de hitos, revisión de esquemas y `CHANGELOG.md`.
2. **Ingeniero de Datos y GIS:** Scripts en `src/etl/` y `src/gis/`, limpieza y validación de las 24 jurisdicciones.
3. **Analista Regulatorio y Negocio:** Matriz fiscal (RIGI, IIBB), proyectos energéticos futuros y supuestos de negocio.
4. **Científico de Datos:** Scoring multicriterio, clustering, Monte Carlo y proyecciones 2028–2036 en `src/modeling/`.
5. **Especialista UX/BI:** Interfaz Streamlit (`app/`) con CSS custom y salidas estructuradas para Power BI.