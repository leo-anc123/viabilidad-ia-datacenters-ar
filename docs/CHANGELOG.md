# Changelog — Viabilidad IA Datacenters AR

Todos los cambios estructurales, ponderaciones modificadas e imputaciones aprobadas
se registran aquí con fecha y rol activo.  
Formato: `[versión] — YYYY-MM-DD | Rol`

---

## [1.0.0] — 2026-11-20 | Especialista UX/BI y Orquestador (PMO)

### Added
- `bi/guia_powerbi_modelo_estrella.md`: manual de ingeniería de BI paso a paso para Power BI Desktop que documenta la conexión de las 4 tablas planas de `data/04_outputs/pbi_ready/` (`dim_jurisdicciones`, `fact_scores_perfiles`, `fact_subscores_radar`, `geo_centrales_sadi`), el esquema de relaciones 1:N estrictas (`jurisdiccion_id`), tipado de datos estricto (códigos INDEC como texto, coordenadas en decimal con categoría geográfica), tabla de medidas DAX (`_Medidas`) lista para producción sin duplicar el motor WSM, y propuesta de layout de 2 páginas ejecutivas dark-mode.
- `bi/theme_dark_ivid.json`: archivo de tema visual oficial dark-mode importable en dos clics en Power BI Desktop, alineado a la paleta ejecutiva (`#0e1117`, `#161b22`, `#38bdf8`, `#fbbf24`, `#34d399`, `#c084fc`, `#f472b6`).
- `docs/assets/`: directorio creado para alojamiento de capturas de pantalla de la aplicación y reportes, con instructivo `docs/assets/README.md` de nomenclatura y resolución recomendada.

### Changed
- `README.md`: reescritura integral de alto impacto para reclutadores y líderes de infraestructura tecnológica, incorporando badges de estado de release, análisis del dilema de negocio (Campus IA 100+ MW vs. Nodos Edge <5 ms), arquitectura end-to-end en diagrama Mermaid, matriz de resultados clave (Top 3 IA vs. Top 3 Edge, 4 Arquetipos K-Means, robustez Monte Carlo 1.000 runs), caja de transparencia metodológica detallando las 13 variables excluidas en NaN sin inventar datos, guía de despliegue en un clic para Streamlit Community Cloud y enlaces a capturas relativas en `docs/assets/`.
- `requirements.txt`: actualizado y auditado formalmente para despliegue en producción en Streamlit Community Cloud (`v1.0.0 — Fase 4 MVP Ready`), verificando la ausencia de dependencias faltantes o incompatibles.
- **Hito:** Cierre formal de la **Fase 4 (MVP de Portafolio v1.0.0)**. El repositorio alcanza el estado de producto completo, reproducible y auditable.

### QA & Validation
- Verificación de no-exclusión en `.gitignore`: 100% de los datasets consumidos por `app/main.py` (`data/03_processed/`, `data/04_outputs/` y `config/`) confirmados como trackeados en Git y no ignorados.
- Coherencia numérica auditada: Santa Cruz (67.00 pts en IA, Rank #1), CABA (81.58 pts en Edge, Rank #1), Tierra del Fuego (PUE climatológico 1.245, 0.0 MW SADI), 39.332,2 MW totales en SADI y 474 centrales CAMMESA validadas.
- Suite de pruebas de regresión completa ejecutada y aprobada al 100%:
  - `src/etl/validate_master.py`: **PASS** (24 filas, 62 columnas, 0 errores, 0 advertencias).
  - `src/modeling/validate_mcda.py`: **PASS** (7/7 pruebas aprobadas).
  - `src/modeling/validate_fase3.py`: **PASS** (clustering K-Means, Monte Carlo y capa BI validadas).
  - `python -m py_compile app/main.py`: **PASS** (código 0).
  - `streamlit.testing.v1.AppTest`: **PASS** (0 excepciones).

---

## [0.8.0] — 2026-11-20 | Especialista UX/BI

### Added
- `.streamlit/config.toml`: archivo de configuración de Streamlit con tema oscuro unificado (`base = "dark"`, fondo `#0e1117`, secundario `#161b22`, primario cian `#38bdf8`) y modo headless para despliegue productivo.
- `app/styles.css`: hoja de estilos CSS ejecutiva dark-mode profesional con diseño a medida para tarjetas KPI (`.kpi-container`), caja metodológica (`.methodology-box`), badges categóricos, microtipografía, ocultamiento de elementos genéricos de Streamlit y compatibilidad de contrastes WCAG.
- `app/main.py`: aplicación web interactiva completa en Streamlit organizada en 4 pestañas analíticas:
  1. *Panel Ejecutivo:* 5 KPIs dinámicos calculados al 100% desde los datos reales (Santa Cruz líder IA con 67.00 pts, CABA líder Edge con 81.58 pts, Tierra del Fuego mejor PUE climatológico a 1.245, 39.332,2 MW SADI y 474 centrales monitoreadas); gráfico Plotly comparativo horizontal del Top 10 (Perfil IA vs. Perfil Edge); y caja de Transparencia Metodológica detallando fuentes auditadas (CAMMESA, SMN, NASA POWER, ENACOM, CEP XXI, INPRES, RIGI) y las 13 variables excluidas por ausencia de fuente abierta sin inventar datos.
  2. *Mapa GIS y Centrales SADI:* mapa interactivo Plotly con `scatter_map` y teselas `carto-darkmatter` (sin token de Mapbox), representando las 474 centrales del SADI dimensionadas por MW y coloreadas por tecnología de generación, con filtros cruzados multiselección por tecnología y provincia, métricas dinámicas de participación renovable y tabla detallada expandible.
  3. *Simulador en Tiempo Real:* selector de 4 casos de uso (Campus IA Training, Nodos Edge, Benchmark CABASE, Personalizado) y 5 sliders dimensionales renormalizados automáticamente a $\sum w = 1.0$ con control de seguridad contra división por cero; cálculo dinámico del ranking en vivo importando directamente `calculate_composite_score()` de `src/modeling/mcda_engine.py` (cero lógica de negocio duplicada); despliegue de provincia ganadora, gráfico Radar (`go.Scatterpolar`) comparando la provincia seleccionada contra el promedio nacional, y tabla de ranking simulado para las 24 jurisdicciones.
  4. *Ciencia de Datos (Arquetipos & Monte Carlo):* visualización de los 4 arquetipos de infraestructura resultantes de K-Means ($k=4$, Silhouette 0.478) mediante gráfico de barras por centroide dimensional y panel explicativo; visualización de la simulación Monte Carlo (1.000 iteraciones con perturbación $\pm 20\%$) mostrando intervalos de confianza P5–P95 y probabilidades empíricas de calificar en Top 3 y Top 5 por jurisdicción.

### QA & Validation
- Verificación de compilación sintáctica `python -m py_compile app/main.py`: **PASS** (código 0).
- Suite automatizada de pruebas con `streamlit.testing.v1.AppTest`: **PASS** (0 excepciones, renderizado completo de gráficos Plotly, mapas, sliders y llamadas a `src.modeling.mcda_engine`).
- Cierre formal del **Bloque 4.1 (Aplicación Web Interactiva Streamlit)** de la Fase 4.

---

## [0.7.0] — 2026-11-20 | Científico de Datos

### Added
- `src/modeling/clustering.py`: módulo de clustering no supervisado (K-Means con semilla reproducible `random_state=42`) sobre los 5 sub-scores dimensionales; barrido de hiperparámetro $k \in [3, 6]$ con evaluación de Silhouette Score e inercia; selección de $k=4$ óptimo de negocio (Silhouette 0.4784) identificando 4 arquetipos de infraestructura con asignación semántica determinística:
  1. *Hub Metropolitano & Conectividad Core* (CABA, Buenos Aires).
  2. *Polo Austral & Free-Cooling Extremo* (Santa Cruz, Tierra del Fuego).
  3. *Corredor Productivo & Energético SADI/Renovable* (16 jurisdicciones: Córdoba, Mendoza, Neuquén, Río Negro, Chubut, etc.).
  4. *Brecha Fiscal e Infraestructura Rezagada* (Formosa, La Pampa, La Rioja, Santiago del Estero).
- `data/04_outputs/clusters_arquetipos.parquet` y `data/04_outputs/clusters_arquetipos.csv`: datasets exportados con identificación de cluster, etiquetas semánticas y descripción de negocio para las 24 jurisdicciones.
- `src/modeling/montecarlo.py`: motor estocástico de simulación Monte Carlo vectorizado (1.000 iteraciones por perfil con semilla fija `seed=42`) aplicando perturbación simétrica de $\pm 20\%$ sobre ponderaciones directivas y renormalización estricta a $\sum w = 1.0$; cálculo de score medio, desviación estándar, intervalo P5–P95, ranking mediano y probabilidades empíricas de calificar en Top 3 y Top 5.
- `data/04_outputs/montecarlo_sensibilidad.parquet` y `data/04_outputs/montecarlo_sensibilidad.csv`: datasets consolidados de sensibilidad y estabilidad de rankings en formato tabular largo y ancho.
- `src/modeling/export_bi_feeds.py`: orquestador de exportación del Modelo Estrella en `data/04_outputs/pbi_ready/` codificado en CSV con BOM (`UTF-8-SIG`) listo para consumo nativo en Power BI y Streamlit:
  - `dim_jurisdicciones.csv` (24 filas × 9 columnas): dimensión con claves INDEC, geografía y arquetipos.
  - `fact_scores_perfiles.csv` (72 filas × 15 columnas): hechos con scores determinísticos, rankings y métricas Monte Carlo de los 3 perfiles.
  - `fact_subscores_radar.csv` (120 filas × 5 columnas): hechos normalizados para gráficos de radar (5 dimensiones por jurisdicción).
  - `geo_centrales_sadi.csv` (474 filas × 11 columnas): capa geoespacial limpia de centrales eléctricas de CAMMESA en EPSG:4326 validadas estrictamente dentro del Bounding Box de Argentina (0 nulos, 0 en 0,0) y mapeadas a `jurisdiccion_id`.
- `src/modeling/validate_fase3.py`: suite automatizada de control de calidad para Fase 3 que valida al 100% la partición de clusters, congruencia estocástica de Monte Carlo e integridad referencial y espacial del Modelo Estrella.
- `docs/resultados_fase3_ml.md`: reporte técnico y ejecutivo exhaustivo resumiendo la justificación matemática de $k=4$, taxonomía de arquetipos, estabilidad estocástica (100% de probabilidad Top 3 para Santa Cruz, Chubut y CABA en Perfil A; 100% para CABA, Buenos Aires y Córdoba en Perfil B) e implicancias estratégicas territoriales.

### Changed
- Cierre formal de la **Fase 3 (Modelado, Clustering y Scoring Multicriterio)**. Pipeline analítico 100% precomputado, desacoplado y listo para alimentar la interfaz Streamlit y los tableros Power BI de la Fase 4.

---

## [0.6.0] — 2026-11-20 | Científico de Datos

### Added
- `src/modeling/__init__.py`: inicializador del paquete de modelado estadístico y scoring MCDA.
- `src/modeling/preprocessing.py`: pipeline de preprocesamiento, aislamiento de 14 features operativas completas, exclusión formal de 13 columnas 100% NaN auditadas sin imputar valores sintéticos, transformación logarítmica (`log1p`) sobre variables con asimetría extrema (`puestos_software_clae62` con skew 4.61 y `sadi_potencia_instalada_mw` con skew 2.58), escalado Min-Max [0, 100], inversión de sentido para variables de costo/riesgo (`pue_climatologico_estimado`, `temp_max_verano_prom_c`, `distancia_las_toninas_km`, `riesgo_sismico_zona`, `iibb_alicuota_tech_pct`), y tratamiento riguroso de la restricción física de Tierra del Fuego (red aislada = 0.0 MW SADI).
- `src/modeling/mcda_engine.py`: motor de scoring multicriterio jerárquico puro (WSM) en dos niveles:
  1. Cálculo de 5 sub-scores dimensionales (0–100): `subscore_energia`, `subscore_clima`, `subscore_conectividad`, `subscore_fiscal`, `subscore_talento_riesgo`.
  2. Validador estricto de pesos (comprobación de no-negatividad y suma = 1.0 con tolerancia 1e-6).
  3. Cálculo de scores compuestos y rankings ordinales unívocos (1 a 24) por perfil de demanda.
- `config/weights_profiles.json`: actualizado a versión 0.6.0 con el esquema formal de 5 macro-dimensiones y parametrización de 3 perfiles contrastantes: `campus_ia_training` (Alta densidad), `nodo_inferencia_edge` (Baja latencia) y `benchmark_cabase` (Línea base sectorial uniforme 20%).
- `data/04_outputs/scores_mcda_perfiles.parquet`: dataset consolidado con las 24 jurisdicciones, los 5 sub-scores dimensionales [0, 100] y el score/ranking de los 3 perfiles de demanda (compresión Snappy).
- `data/04_outputs/scores_mcda_perfiles.csv`: archivo espejo en CSV (UTF-8 con BOM) para visualización inmediata en Excel y conexión a Power BI.
- `src/modeling/validate_mcda.py`: suite de pruebas estadísticas y de integridad con 7 validaciones automáticas pasando al 100% (rango [0, 100], 0 NaNs, consistencia de rankings 1..24, validación de tolerancias de pesos y persistencia).
- `docs/resultados_mcda_v1.md`: reporte analítico ejecutivo detallando los rankings Top 10 y Bottom 5, análisis de sensibilidad entre entrenamiento vs. inferencia edge, y diagnóstico territorial de Patagonia, AMBA, Cuyo y Centro.

### Changed
- Cierre exitoso del **Bloque 3.1 (Preprocesamiento y Motor MCDA)** de la Fase 3. Código desacoplado y preparado para ser importado por los sliders de Streamlit en la Fase 4.

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
