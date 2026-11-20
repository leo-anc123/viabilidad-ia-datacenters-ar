# Changelog — Viabilidad IA Datacenters AR

Todos los cambios estructurales, ponderaciones modificadas e imputaciones aprobadas
se registran aquí con fecha y rol activo.  
Formato: `[versión] — YYYY-MM-DD | Rol`

---

## [0.2.0] — 2026-11-20 | Ingeniero de Datos y GIS

### Added
- `data/02_interim/jurisdicciones_base.csv`: tabla ancla territorial con exactamente
  24 filas (23 provincias + CABA), códigos INDEC de 2 dígitos (zero-padded),
  nombres oficiales normalizados, macrorregiones (AMBA unificada, NOA, NEA, Cuyo,
  Centro, Patagonia) y coordenadas de capitales en EPSG:4326 (WGS84 / IGN).
  Distribución: AMBA×2, Centro×4, Cuyo×3, NEA×4, NOA×6, Patagonia×5.
- `src/etl/build_jurisdicciones_base.py`: script ETL reproducible que genera y
  auto-valida `jurisdicciones_base.csv`. Incluye 7 checks internos de integridad
  (conteo de filas, tipos, formato de IDs, ausencia de nulos, rangos WGS84).
  Salida: UTF-8-BOM, compatible con Excel y Power BI.
- `docs/data_dictionary.md`: diccionario de datos con esquema objetivo completo
  de `master_24_jurisdicciones.parquet`. 6 secciones, ~19 variables modeladas.
  Columnas de Fases 3-5 marcadas como 🔴 NaN o 🟡 PROXY — cero datos inventados.
  Incluye tabla de registro de variables NaN/PROXY con próximos pasos y bloque
  responsable para cada una.
- `src/etl/validate_master.py`: auditor automático de calidad reutilizable.
  7 checks: conteo de filas, columnas requeridas, duplicados, match contra ancla
  INDEC, tipos de dato, % nulos por columna y coordenadas en rango WGS84.
  Uso CLI: `python src/etl/validate_master.py <archivo> [--ancla <path>] [--quiet]`.
  Retorna dict `{status, errors, warnings, null_report}` para uso programático.
  Exit code 0 (PASS) / 1 (FAIL) para integración CI/CD.
  Prueba de integración ejecutada: PASS — 7/7 checks, 0 advertencias.

### Notes
- `jurisdiccion_corta` de Santiago del Estero: "Stgo. Estero" (aprobado en plan).
- `jurisdiccion_nombre` de Tierra del Fuego: nombre corto (sin "Antártida e Islas...").
- Región AMBA unifica CABA + Provincia de Buenos Aires como región de análisis.

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
