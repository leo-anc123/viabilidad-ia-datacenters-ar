# Viabilidad de Data Centers y Campus de IA en Argentina

> **Estado actual:** 🟡 Fase 1 — Inicialización y estructura base del repositorio

## Descripción

Proyecto de Ciencia de Datos de nivel portafolio orientado a determinar la **viabilidad técnica, energética, geoespacial, climática y regulatoria** para radicar Data Centers tradicionales y Campus de Inteligencia Artificial en las **24 jurisdicciones de Argentina** (23 provincias + CABA).

El análisis modela dos perfiles de demanda diferenciados mediante un índice multicriterio (MCDA):

| Perfil | Nombre | Prioridades |
|---|---|---|
| **A** | Campus de Entrenamiento IA — Alta Densidad | Disponibilidad SADI, eficiencia térmica (PUE / free cooling), agua, fiscal (RIGI). Tolerante a latencia. |
| **B** | Nodos de Inferencia / Edge | Baja latencia, cercanía a IXPs y cables submarinos, densidad de fibra, capital humano IT. |

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje & ETL | Python 3.13, Pandas, NumPy, PyArrow (Parquet) |
| Modelado | Scikit-learn (clustering, escalado), SciPy / Monte Carlo |
| GIS | GeoPandas, Shapely, Folium — EPSG:4326 (Fase 3) |
| Dashboard | Streamlit + Plotly (dark-mode ejecutivo) |
| BI | Power BI (consumiendo `data/04_outputs/pbi_ready/`) |
| Config | YAML + JSON (`config/`) |

---

## Fases del Proyecto

| Fase | Nombre | Estado |
|---|---|---|
| **Fase 1** | Inicialización — estructura base, config y datos | 🟡 En curso |
| **Fase 2** | ETL & Tabla Maestra de las 24 jurisdicciones | ⬜ Pendiente |
| **Fase 3** | GIS, scoring MCDA y clustering | ⬜ Pendiente |
| **Fase 4** | Dashboard Streamlit + exports Power BI | ⬜ Pendiente |
| **Fase 5** | Simulador CAPEX/OPEX, RIGI y proyecciones 2028–2036 | ⬜ Pendiente |

---

## Arquitectura del Pipeline

```
data/01_raw/          ← Fuentes oficiales (CAMMESA, INDEC, ENACOM, etc.)
      │
      ▼
data/02_interim/      ← Limpieza, normalización de nombres y jurisdiccion_id (INDEC)
      │
      ▼
data/03_processed/    ← Tabla maestra (24 jurisdicciones × dimensiones) + GeoJSON EPSG:4326
      │
      ▼
data/04_outputs/      ← Scores MCDA, clusters, resultados Monte Carlo
      └── pbi_ready/  ← Tablas planas para consumo directo en Power BI
```

---

## Reglas de Calidad de Datos (resumen)

1. **Cero datos inventados** — valores faltantes se dejan como `NaN` y se documentan.
2. **`data/01_raw/` es de sólo lectura** — toda transformación parte desde `02_interim/`.
3. **Clave estándar única:** `jurisdiccion_id` (código INDEC 2 dígitos) + `jurisdiccion_nombre`.
4. **Proyección espacial:** EPSG:4326 (WGS84) en todas las capas geográficas.
5. **Trazabilidad:** todo dataset en `config/data_sources.yaml`.
6. **Separación lógica/UI:** cálculos en `src/modeling/`, nunca en Streamlit ni DAX.

> Ver `AGENTS.md §4` para el detalle completo.

---

## Setup del Entorno

```bash
# 1. Activar el entorno virtual
# Windows:
.venv\Scripts\activate

# 2. Instalar dependencias base
pip install -r requirements.txt

# 3. Verificar instalación
python -c "import pandas, numpy, streamlit, plotly, sklearn; print('OK')"
```

---

## Estructura del Repositorio

```
viabilidad-ia-datacenters-ar/
├── agents/          # Instrucciones modulares por rol y contratos I/O
├── config/          # data_sources.yaml + weights_profiles.json
├── data/
│   ├── 01_raw/      # SOLO LECTURA — datos crudos descargados
│   ├── 02_interim/  # Limpieza intermedia
│   ├── 03_processed/# Tabla maestra y capas GeoJSON
│   └── 04_outputs/  # Scores, clusters, Monte Carlo
│       └── pbi_ready/
├── src/
│   ├── etl/         # Extracción y limpieza
│   ├── gis/         # Procesamiento geoespacial
│   ├── modeling/    # Motor MCDA, clustering, Monte Carlo
│   └── finance/     # [Fase 5] Simulador CAPEX/OPEX y RIGI
├── app/             # Aplicación Streamlit + CSS custom
├── bi/              # Documentación Power BI (medidas DAX)
├── notebooks/       # EDA y validación estadística
├── docs/            # Diccionario de datos, metodología, CHANGELOG
├── AGENTS.md        # Roles, arquitectura y gobernanza del proyecto
├── requirements.txt
└── README.md
```

---

## Autor

Leandro — Proyecto de portafolio de Ciencia de Datos | 2026
