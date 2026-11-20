# Changelog — Viabilidad IA Datacenters AR

Todos los cambios estructurales, ponderaciones modificadas e imputaciones aprobadas
se registran aquí con fecha y rol activo.  
Formato: `[versión] — YYYY-MM-DD | Rol`

---

## [0.1.0] — 2026-11-19 | Orquestador (PMO)

### Added
- `AGENTS.md`: contexto del proyecto, stack tecnológico, arquitectura de carpetas
  (contrato §3), reglas de calidad de datos (§4) y gobernanza (§5).
  Roles lógicos definidos: Orquestador, Ing. Datos/GIS, Analista Regulatorio,
  Científico de Datos, Especialista UX/BI.
- Estructura base de carpetas según contrato `AGENTS.md §3` (Hito 0 / Fase 1):
  `agents/`, `config/`, `data/{01_raw,02_interim,03_processed,04_outputs/pbi_ready}`,
  `src/{etl,gis,modeling,finance}`, `app/`, `bi/`, `notebooks/`, `docs/`.
  Archivos `.gitkeep` en todas las carpetas vacías para trazabilidad en Git.
- `.gitignore`: Python, `.venv/`, Jupyter checkpoints, Power BI binarios (`.pbix/.pbit`),
  archivos de SO, secretos, IDEs. `data/01_raw/` completo excluido (excepto `.gitkeep`).
- `requirements.txt` base (Fases 1–2): `pandas`, `numpy`, `pyarrow`, `pyyaml`,
  `requests`, `openpyxl`, `streamlit`, `plotly`, `scikit-learn`.
  GIS y Monte Carlo reservados para Fase 3.
- `config/data_sources.yaml`: plantilla vacía con esquema de trazabilidad obligatorio
  (nombre, dimension, fuente_oficial, url, fecha_corte, periodicidad, estado, notas).
- `config/weights_profiles.json`: perfiles borrador Perfil A (`campus_ia_training`,
  suma=1.00) y Perfil B (`nodo_inferencia_edge`, suma=1.00).
- `README.md`: descripción ejecutiva, perfiles A/B, arquitectura del pipeline,
  stack tecnológico, tabla de fases y reglas de calidad resumidas.
- Entorno virtual `.venv` verificado (Python 3.13.1 / pip 24.3.1).
  Dependencias NO instaladas — pendiente de ejecución manual tras aprobación.
