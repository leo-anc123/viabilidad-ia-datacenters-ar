# Changelog — Viabilidad IA Datacenters AR

Todos los cambios estructurales, ponderaciones modificadas e imputaciones aprobadas
se registran aquí con fecha y rol activo.  
Formato: `[versión] — YYYY-MM-DD | Rol`

---

## [0.5.0] — 2026-11-20 | Analista Regulatorio y Negocio / Ingeniero de Datos y GIS

### Added
- `docs/supuestos_regulatorios.md`: marco normativo y respaldo documental exhaustivo de las 24 jurisdicciones argentinas para el Régimen de Incentivo para Grandes Inversiones (RIGI, Ley 27.742) y las alícuotas referenciales de Ingresos Brutos (IIBB) sobre software y servicios tecnológicos bajo Leyes de Economía del Conocimiento.
- `src/etl/build_fiscal_regulatoria.py`: script ETL reproducible para la construcción y validación de la dimensión fiscal y regulatoria.
- `data/02_interim/dim_fiscal_regulatoria.csv`: tabla interim de 24 jurisdicciones con métricas normativas:
  `rigi_adhesion` (18 provincias adheridas por ley, 6 no adheridas), `rigi_normativa`, `rigi_fecha_sancion`,
  `iibb_alicuota_tech_pct` (0.0% para promovidas; 3.0%–3.5% para alícuota general), `iibb_regimen_promocion`,
  `indice_promocion_fiscal` (score 0–10 ponderando gran inversión y fomento IIBB, reconociendo el Régimen de la Ley 19.640 de Tierra del Fuego y el RPI de Buenos Aires) y `estado_verificacion_normativa` (`verificado_oficial`). Variable `iibb_alicuota_energia_pct` documentada formalmente en NaN auditable.
- `src/etl/build_master_table.py`: script de consolidación maestra que ejecuta el cruce 1:1 sobre `jurisdiccion_id` entre `jurisdicciones_base.csv` y las 5 tablas dimensionales (`dim_energia_sadi.csv`, `dim_clima_agua.csv`, `dim_conectividad.csv`, `dim_talento_riesgo.csv` y `dim_fiscal_regulatoria.csv`).
- `data/03_processed/master_24_jurisdicciones.parquet`: tabla maestra oficial consolidada (24 filas × 62 columnas), con tipado estricto y compresión Snappy.
- `data/03_processed/master_24_jurisdicciones.csv`: copia espejo en formato CSV (UTF-8 con BOM) para visualización inmediata en Excel y Power BI.
- `docs/qa_report_fase2.md`: reporte formal de control de calidad y cobertura de Fase 2, con auditoría exhaustiva columna por columna: 48 columnas 100% completas, 1 columna con nulos parciales justificados de negocio (`rigi_fecha_sancion`) y 13 columnas 100% NaN documentadas sin inventar datos para Fases 3 a 5.
- `config/data_sources.yaml`: incorporadas las fuentes oficiales de RIGI (Secretaría de Inversiones) y administraciones tributarias provinciales para la dimensión fiscal.
- `docs/data_dictionary.md`: actualizado a versión 0.5.0 reflejando el estado de la dimensión fiscal y la unificación de la tabla maestra.

### QA & Validation
- Ejecutado `src/etl/validate_master.py` sobre `data/02_interim/dim_fiscal_regulatoria.csv`: **PASS** (24 filas, 0 errores, match 100% ancla).
- Ejecutado `src/etl/validate_master.py` sobre `data/03_processed/master_24_jurisdicciones.parquet`: **PASS** (24 filas, 62 columnas, 0 errores, 0 advertencias, coordenadas WGS84 e IDs INDEC verificados).
- Ejecutado `src/etl/validate_master.py` sobre `data/03_processed/master_24_jurisdicciones.csv`: **PASS** (24 filas, 62 columnas, 0 errores, 0 advertencias).
- Cierre formal de la **Fase 2 (Ingesta, Limpieza y Master Data)**. Pipeline listo para la Fase 3 (Modelado, Clustering y Scoring Multicriterio).

---

## [0.4.0] — 2026-11-20 | Ingeniero de Datos y GIS

### Added
- `src/gis/fetch_conectividad.py`: script GIS/ETL para cálculo de distancias geodésicas (Haversine WGS84) e ingesta de conectividad provincial ENACOM.
- `data/01_raw/enacom_internet_tecnologias_raw.csv`: archivo crudo ENACOM con accesos a internet fijo desglosados por tecnología (FTTH, cablemódem, ADSL, etc.) hasta 2026-T2.
- `data/01_raw/enacom_internet_penetracion_raw.csv`: archivo crudo ENACOM con penetración cada 100 hogares y 100 habitantes hasta 2026-T2.
- `data/01_raw/enacom_internet_velocidad_raw.csv`: archivo crudo ENACOM con velocidad media de descarga provincial (Mbps) hasta 2026-T2.
- `data/02_interim/dim_conectividad.csv`: tabla de 24 jurisdicciones con métricas calculadas:
  `distancia_las_toninas_km` (Haversine exacto a `-36.487, -56.696`), `fibra_optica_accesos`, `fibra_optica_pct`,
  `penetracion_hogares_pct`, `penetracion_habitantes_pct` y `velocidad_media_bajada_mbps`.
  Variables `ixp_cabase_nodos` (sin API/CSV público) y `fibra_troncal_cobertura_score` dejadas en NaN explícito auditable.
- `src/etl/fetch_talento_riesgo.py`: script ETL para ingesta y cálculo de métricas de capital humano IT (CEP XXI) y consulta programática al servicio oficial de zonificación sísmica del INPRES (Reglamento CIRSOC 103).
- `data/01_raw/cepxxi_puestos_trabajo_clae2_provincias_raw.csv`: panel mensual del CEP XXI (Ministerio de Economía) de puestos registrados por provincia y CLAE a 2 dígitos (corte 2023-11-01).
- `data/01_raw/inpres_zonificacion_24_raw.json`: payload crudo consolidado con las 24 respuestas del servicio web oficial del INPRES (`zonas_result.php`) para las capitales provinciales.
- `data/02_interim/dim_talento_riesgo.csv`: tabla de 24 jurisdicciones con métricas calculadas:
  `puestos_privados_totales`, `puestos_software_clae62` (CLAE 62), `puestos_tic_clae61_63` (CLAE 61-63),
  `pct_empleo_tic_privado` (tasa sin comprimir para escalado robusto), `densidad_stem_it_score` (normalizado 0–10 a CABA)
  y `riesgo_sismico_zona` (0 a 4 oficial INPRES). Variables `graduados_stem_anual`, `riesgo_climatico_score`
  y `riesgo_combinado_score` dejadas en NaN explícito auditable.
- `config/data_sources.yaml`: incorporadas 5 fuentes con metadata de trazabilidad (ENACOM tecnologías, penetración, velocidad, CEP XXI puestos e INPRES CIRSOC 103, más entradas borrador para CABASE y SPU).
- `docs/data_dictionary.md`: actualizado a versión 0.4.0 reflejando los nuevos estados 🟢 LISTO y 🔴 NaN de las Secciones 3 y 5.

### QA & Validation
- Ejecutado `src/etl/validate_master.py` sobre `data/02_interim/dim_conectividad.csv`:
  **PASS** (24/24 filas, match ancla INDEC, 0 duplicados, 0% nulos en distancias y métricas ENACOM, 100% nulo documentado en CABASE).
- Ejecutado `src/etl/validate_master.py` sobre `data/02_interim/dim_talento_riesgo.csv`:
  **PASS** (24/24 filas, match ancla INDEC, 0 duplicados, 0% nulos en variables de empleo CEP XXI y riesgo sísmico INPRES, 100% nulo documentado en SPU y riesgo climático).

---

## [0.3.0] — 2026-11-20 | Ingeniero de Datos y GIS

### Added
- `src/gis/fetch_clima_pue.py`: script ETL para ingesta y cálculo de métricas climáticas
  a partir de la API histórica de Open-Meteo (reanálisis ERA5 / ECMWF 2000–2023, 8.766 días
  por capital provincial).
- `data/01_raw/clima_24_jurisdicciones_raw.json`: respuesta cruda de Open-Meteo para las 24
  coordenadas geográficas oficiales de las capitales argentinas (cero errores de red).
- `data/02_interim/dim_clima_agua.csv`: tabla de 24 jurisdicciones con métricas calculadas:
  `temp_media_anual_c`, `temp_max_verano_prom_c` (DJF), `horas_free_cooling_estimadas`
  (umbral Tbs < 15 °C según ASHRAE 90.4-2019, anualizadas con factor horario 0.70) y
  `pue_climatologico_estimado` (interpolación entre 1.58 y 1.10 según Uptime Institute).
  Variable `indice_estres_hidrico` dejada explícitamente en NaN por requerir descarga
  manual desde WRI Aqueduct 4.0.
- `src/etl/fetch_energia_sadi.py`: script ETL que descarga y procesa datos abiertos de la
  Secretaría de Energía / CAMMESA (`datos.energia.gob.ar`).
- `data/01_raw/cammesa_centrales_generacion_sadi_raw.csv`: archivo crudo de 474 centrales
  eléctricas en el SADI con geolocalización, tecnología y potencia nominal en MW.
- `data/01_raw/cammesa_potencia_instalada_raw.csv`: serie histórica mensual CAMMESA.
- `data/01_raw/minem_renovar_mater_raw.csv`: catálogo geolocalizado de proyectos RenovAr / MATER.
- `data/02_interim/dim_energia_sadi.csv`: tabla de 24 jurisdicciones con `sadi_potencia_instalada_mw`
  y `sadi_pct_renovable` (Ley 27.191). Variables `sadi_uptime_index` (ENRE solo cubre AMBA),
  `sadi_margen_disponible_mw`, proyecciones 2028/2036 y potencial off-grid documentadas
  en NaN de acuerdo a las reglas de calidad de datos. Tierra del Fuego computa 0.0 MW
  por constituir un subsistema provincial aislado no interconectado.
- `config/data_sources.yaml`: incorporadas 5 fuentes de datos con metadata completa de trazabilidad.

### QA & Validation
- Ejecutado `src/etl/validate_master.py` sobre `data/02_interim/dim_clima_agua.csv`:
  **PASS** (24/24 filas, match ancla INDEC, 0% nulos en clima y PUE, 100% nulo documentado en hídrico).
- Ejecutado `src/etl/validate_master.py` sobre `data/02_interim/dim_energia_sadi.csv`:
  **PASS** (24/24 filas, match ancla INDEC, 0% nulos en potencia y % renovable).

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
