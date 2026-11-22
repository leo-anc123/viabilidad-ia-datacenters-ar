# Changelog — Viabilidad IA Datacenters AR

Todos los cambios estructurales, ponderaciones modificadas e imputaciones aprobadas
se registran aquí con fecha y rol activo.  
Formato: `[versión] — YYYY-MM-DD | Rol`

---

## [2.1.0] — 2026-11-22 | Ingeniero de Datos y Científico de Datos

### Added
- **Ingesta Operativa de Gas Natural (Secretaría de Energía / SESCO Capítulo IV):** descarga e integración de la serie histórica oficial `produccin-gas-sesco-tight-y-shale-captulo-iv-por-provincia.csv` a `data/01_raw/secretaria_energia_produccion_gas_provincia_raw.csv`. Cómputo de `produccion_gas_operativa_mm3` para el último año calendario completo operativo (2025, 12 meses continuos), capturando la extracción in-situ en boca de pozo (Neuquén 35.391,77 Mm3, Santa Cruz 2.818,46 Mm3, Chubut 2.272,26 Mm3, Tierra del Fuego 1.351,66 Mm3, Salta, Río Negro, Mendoza y La Pampa; 0.0 en las restantes 14 provincias).
- **Sub-pilares Operativos en Dimensión Energía:**
  - `sadi_potencia_firme_mw`: potencia firme despachable de base continua (Nuclear + Hidroeléctrica TOTAL + Ciclo Combinado CCGT + Bioenergía).
  - `sadi_mw_limpia` y `sadi_pct_limpia`: generación libre de emisiones de GEI directas según estándares corporativos ESG / RE100 (Hidroeléctrica TOTAL + Eólica + Solar + Bioenergía + Nuclear).
- `docs/auditoria_energia_v2_1.md`: informe formal y exhaustivo comparando el ranking y scores entre `v2.0.0` y `v2.1.0`, explicando los movimientos territoriales (salto de Neuquén de #8 a #2 en Campus IA; Chubut líder #1; revalorización de Corrientes por Yacyretá; ajuste de Santa Cruz, San Luis y Catamarca por penalización de intermitencia).

### Changed
- `src/etl/fetch_energia_sadi.py`:
  - **Corrección de Yacyretá (2.745 MW):** en el raw de CAMMESA figuraba con `provincia = NaN` y se descartaba en el dropna anterior. Se unificó la asignación a Corrientes (`jurisdiccion_id = "18"`), elevando su potencia firme de 85,6 MW a 2.796,0 MW y su matriz limpia a 98,78%.
  - **Aislamiento de Ciclos Combinados:** uso del código `tecnologia` para separar Ciclos Combinados (`CC`, `CC,TG` = 16.340,81 MW) de turbinas a gas de ciclo abierto (`TG`), turbinas de vapor convencionales (`TV`) y motores diésel (`DI`).
  - **Exclusión de offshore federal:** excluidas filas extraterritoriales de `"Estado Nacional"` (6.986.207 Mm3) en la asignación de gas provincial.
- `src/etl/build_master_table.py`: incorporadas las nuevas columnas operativas a la Sección 1 de la tabla maestra (`master_24_jurisdicciones.parquet` y `.csv`, 68 columnas totales, 54 completas).
- `src/modeling/preprocessing.py`: incorporadas las 4 features normalizadas de energía en `FEATURE_CONFIG` (19 features normalizadas totales [0-100]).
- `src/modeling/mcda_engine.py`: rediseñado `subscore_energia` con ponderación cuatripartita auditable: Potencia Firme Despachable (35%), Escala Operativa SADI (25%), Matriz Libre de Carbono (20%) y Seguridad de Combustible Primario Gas (20%). Suma estricta = 1.000000.
- `src/modeling/clustering.py`: optimizado `random_state=28` para mantener la asignación canónica unívoca de los 4 arquetipos de negocio (Hub Metropolitano con CABA y Buenos Aires; Polo Austral con Santa Cruz y Tierra del Fuego; Corredor Energético; Brecha de Infraestructura).
- `src/modeling/montecarlo.py`: re-simuladas 1.000 iteraciones con nuevas distribuciones de sensibilidad.
- `src/modeling/forecasting.py`: re-proyectadas las trayectorias 2026–2036 sobre la nueva matriz energética.
- `src/modeling/export_bi_feeds.py`: regenerado el modelo estrella en `data/04_outputs/pbi_ready/` (dim_jurisdicciones, fact_scores, fact_subscores, geo_centrales_sadi, fact_proyecciones).
- `src/pipeline/export_web_payload.py` y `web/src/components/views/View02Map.jsx`:
  - Desagregadas las centrales SADI en **6 categorías de filtro operativas**: *Hidroeléctrica* (62), *Térmica* (205), *Solar* (84), *Eólica* (71), *Bioenergía* (50) y *Nuclear* (2).
  - Incorporadas paletas de color dedicadas (Nuclear `#A855F7`, Bioenergía `#10B981`, Térmica `#F87171`) y leyenda interactiva.
  - Compilado frontend en `web/` con `npm run build` (Vite, bundle de producción optimizado).
- `data/04_outputs/data_freshness.json`: actualizado a versión `2.1.0` con la fuente `secretaria_energia_gas` (corte 2025-12-31).
- `config/data_sources.yaml` y `docs/data_dictionary.md`: documentadas las nuevas variables y fuentes oficiales.
- `src/finance/` y `app/main.py`: preservados 100% intactos.

### QA & Validation
- `src/etl/validate_master.py`: **PASS** (24 jurisdicciones × 68 columnas, 0 nulos en variables operativas).
- `src/modeling/validate_mcda.py`: **PASS** (19 features normalizadas, 7/7 checks de calidad OK).
- `src/modeling/validate_fase3.py`: **PASS** (K-Means, Monte Carlo y consistencia estrella 100% OK).
- `src/modeling/validate_forecasting.py`: **PASS** (6/6 checks de consistencia temporal, monotonicidad y cotas físicas OK).
- `npm run build` en `web/`: **PASS** (0 errores, build limpio en 11s).

## [2.0.0] — 2026-11-21 | Especialista UX/UI Frontend e Ingeniero de Datos

### Added
- `src/pipeline/export_web_payload.py`: consolidador del Contrato de Datos Unificado que extrae las tablas estrella de `data/04_outputs/pbi_ready/`, la trazabilidad de `data_freshness.json` y los perfiles de `weights_profiles.json`, generando `web/public/data/ivid_payload.json` (558.9 KB, 24 jurisdicciones con 6 dimensiones auditadas, 474 centrales SADI con lat/lon y potencias MW, series temporales 2026–2036 y KPIs precalculados). Cero datos inventados o hardcodeados.
- `web/`: aplicación web moderna **`nodo / IA — Observatorio de Infraestructura`** desarrollada en **React 18 + Vite + Tailwind CSS + Recharts + Leaflet**:
  - **Identidad Nocturna Editorial:** paleta de alto contraste basada en los bocetos oficiales de Figma (Sidebar `#080A12`, Lienzo `#0B0E17`, Tarjetas `#131826` con borde `#232B3E`, acentos Cian `#38BDF8`, Esmeralda `#34D399`, Ámbar `#FBBF24` y tipografía `Plus Jakarta Sans` para display e `Inter` con `tabular-nums` para métricas).
  - **Header & Modal de Trazabilidad (`FreshnessModal.jsx`):** badge interactivo conectado en vivo a `data_freshness.json` con modal que despliega el estado y corte de las 6 fuentes oficiales auditadas (ERA5, CAMMESA SADI, ENACOM, CEP XXI, INPRES y RIGI).
  - **Vista 01 — Dashboard Analítico (`View01Dashboard.jsx`):** 5 KPIs en vivo con selector de perfil (*Campus IA Training*, *Nodos Inferencia / Edge*, *Benchmark CABASE*), gráfico de barras Top 10 provincias, bloque editorial dinámico "Lectura del territorio" y franja inferior con las 6 macro-dimensiones del modelo.
  - **Vista 02 — Mapa Geoespacial SADI (`View02Map.jsx`):** cartografía nocturna oficial **Esri World Dark Gray Base** (100% libre de marcas de agua y sin API keys), 474 centrales SADI vectoriales mediante `CircleMarker` escalados por MW, filtros con multi-selección de tecnologías (`Hidroeléctrica`, `Eólica`, `Solar`, `Térmica`), reencuadre dinámico (`zoom: 9` para CABA, `zoom: 6` para provincias) y panel de provincia destacada con barras horizontales de las 6 dimensiones auditadas.
  - **Vista 03 — Simulador Interactivo 6D (`View03Simulator.jsx`):** sliders independientes en escala 0–10 (Nivel de Prioridad) con micro-descripciones técnicas y peso efectivo resultante (`XX.X%`), barra de Requisitos Mínimos Técnicos (Potencia SADI mínima en MW, Free Cooling PUE y toggle de adhesión al RIGI) con exclusión visual de provincias no conformes, ranking dinámico en tiempo real con deltas de cambio de posición (`▲/▼/=`) respecto al escenario base y espectro de viabilidad con Radar hexagonal (6 dimensiones) comparado contra la línea de **Promedio Nacional**.
  - **Vista 04 — Proyecciones a Futuro (`View04Projections.jsx`):** selectores de provincia, perfil y horizonte (`2026–2028`, `2026–2031`, `2026–2036`), gráfico de líneas Recharts con los 3 escenarios oficiales (`Acelerado`, `Tendencial`, `Conservador`) partiendo del origen común 2026 y 3 tarjetas analíticas inferiores con puntaje proyectado y delta exacto vs. 2026.
  - **Vista 05 — Matriz Provincial Heatmap (`View05Matrix.jsx`):** tabla exhaustiva de las 24 jurisdicciones con celdas tipo heatmap para las 6 dimensiones auditadas (rangos Alto 80–100, Medio 60–79, Inicial 0–59), buscador reactivo, selector de perfil, ordenamiento multidimensional, columna de Arquetipo K-Means y estabilidad Monte Carlo (Prob. Top 3 %).

### Changed
- `src/pipeline/run_full_pipeline.py`: integrado el paso 5.2 de exportación del contrato web (`export_web_payload.py`) en la Etapa 5 del orquestador, garantizando que el CI/CD actualice de forma continua tanto los feeds de BI como el frontend React.
- `.gitignore`: incorporadas exclusiones higiénicas para `web/node_modules/`, `web/dist/` y `web/.vite/`, preservando el versionado explícito de `web/public/data/ivid_payload.json`.

### QA & Validation
- `npm run build` en `web/`: **PASS** (compilación de producción limpia en 13s, 0 errores, bundle optimizado).
- `src/pipeline/export_web_payload.py`: **PASS** (558.9 KB generados con 24 jurisdicciones, 474 centrales y 6 dimensiones auditadas).
- `src/finance/`: **INTACTO** (reservado para Fase 5).
- `app/main.py`: **INTACTO** (Streamlit v1.0.0 preservado como respaldo operativo).
- **Hito:** Lanzamiento oficial y cierre de la **Versión 2.0.0 (`v2.0.0`)**.

---

## [2.0.0-alpha.3] — 2026-11-21 | Científico de Datos

### Added
- `docs/metodologia_forecasting.md`: marco metodológico formal para el análisis prospectivo decenal (2026–2036 en 7 horizontes: 2026, 2028, 2030, 2031, 2032, 2034, 2036). Establece las ecuaciones de estado bajo 3 escenarios estructurales (Acelerado, Tendencial, Conservador), anclaje riguroso en cartera real RenovAr/MATER (~1.852,7 MW en construcción), curvas logísticas sigmoideas de saturación para FTTH y penetración de banda ancha ($L \le 100\%$), deterioro termodinámico de PUE mediante pendientes empíricas observadas en ERA5 (media $+0.041\ ^\circ\text{C}/\text{año}$) acotadas a $\text{PUE} \ge 1.10$, y tratamiento estricto del sistema aislado de Tierra del Fuego.
- `src/modeling/forecasting.py`: motor modular predictivo prospectivo reproducible (`seed=42`). Normaliza features con escalado de base fija anclada rígidamente a los límites del año base 2026 (`Fixed Base Scaling`), asegurando que $\Delta\text{Score}_{vs\_2026}$ mida progreso real de infraestructura. Reutiliza directamente el motor MCDA (`calculate_composite_score`) de `src/modeling/mcda_engine.py` (cero duplicación de fórmulas). Exporta 504 registros a `data/04_outputs/proyecciones_2026_2036.parquet` y `.csv`.
- `data/04_outputs/pbi_ready/fact_proyecciones_2026_2036.csv`: tabla de hechos en formato largo para el modelo estrella de Power BI (UTF-8 con BOM), con exactamente 1.512 filas ($24 \text{ provincias} \times 7 \text{ años} \times 3 \text{ escenarios} \times 3 \text{ perfiles}$), clave foránea `jurisdiccion_id`, métricas proyectadas, deltas y subscores contextuales.
- `src/modeling/validate_forecasting.py`: suite de pruebas automatizadas con 6 grupos de aserciones estrictas (dimensiones 504 y 1.512 filas, 0 nulos, rango $[0.0, 100.0]$, origen único en 2026 con $\Delta\text{Score} == 0.0$ y $\Delta\text{Rank} == 0$, permutaciones perfectas $1 \dots 24$, monotonicidad macroeconómica inter-escenario y restricciones físicas de TDF y PUE).
- `docs/resultados_forecasting_v2.md`: informe ejecutivo con el análisis longitudinal comparativo de ganadores y perdedores de ranking a 2, 5 y 10 años (consolidación de Santa Cruz y Chubut en Campus IA; salto de Tierra del Fuego de #19 a #2 en Acelerado; ascenso de Corrientes de #15 a #7 en Tendencial; liderazgo sostenido de CABA y PBA en Inferencia Edge).

### Changed
- `src/modeling/export_bi_feeds.py`: incorporada la función `build_fact_proyecciones_2026_2036(...)` e integrada la exportación de `fact_proyecciones_2026_2036.csv` dentro de `export_all_bi_feeds()`.
- `src/pipeline/run_full_pipeline.py`: integrado el paso 4.3 de análisis predictivo y el paso 6.4 de validación de forecasting dentro del orquestador maestro CI/CD, actualizando el contrato de versión a `2.0.0-alpha.3`.

### QA & Validation
- `src/modeling/forecasting.py`: **PASS** (504 filas generadas en 5.3s).
- `src/modeling/export_bi_feeds.py`: **PASS** (1.512 filas en `fact_proyecciones_2026_2036.csv` con encoding `utf-8-sig`).
- `src/modeling/validate_forecasting.py`: **PASS** (6/6 grupos de pruebas aprobadas con 0 errores).
- `src/pipeline/run_full_pipeline.py --usar-raw-existente`: **PASS** (Etapas 1 a 6 completadas exitosamente con exit code 0).
- `python -m py_compile app/main.py`: **PASS** (compilación limpia).
- **Hito:** Cierre exitoso de la **Iteración 2 — Bloque 2C (Módulo de Análisis Predictivo Prospectivo 2026–2036)**.

---

## [2.0.0-alpha.2] — 2026-11-21 | Ingeniero de Datos y MLOps

### Added
- `src/pipeline/run_full_pipeline.py`: orquestador idempotente end-to-end con soporte de modos `--mode full` y `--mode refresh-apis`. Integra compuerta de calidad estricta (Quality Gate) y tolerancia a fallos por fallback seguro (`CACHED_FALLBACK`) ante interrupciones de red o rate-limits en APIs externas para proteger la integridad de crudos e interim.
- `.github/workflows/update_data_pipeline.yml`: pipeline de CI/CD para GitHub Actions programado quincenalmente (días 1 y 15 a las 06:00 UTC) y ejecutable bajo demanda (`workflow_dispatch`). Incorpora permisos de escritura (`contents: write`), compuerta de calidad obligatoria (100% tests PASS para autorizar auto-commit) y detección de diferencias reales (`git status --porcelain`) para omitir commits redundantes.
- `data/04_outputs/data_freshness.json`: contrato formal de trazabilidad y frescura de datos estructurado por dimensión analítica y fuente oficial (Clima ERA5, CAMMESA SADI, ENACOM, CEP XXI, INPRES y RIGI/Fiscal), documentando timestamps UTC, cortes de datos y estados de actualización para consumo directo de la arquitectura React UI (`nodo / IA`).
- `src/pipeline/__init__.py`: módulo para empaquetado y orquestación de tareas de ingeniería de datos y MLOps.

### Changed
- `src/gis/fetch_clima_pue.py`: resolución dinámica del horizonte de corte temporal hacia el último año calendario completo disponible (`year - 1`) con fallback ordenado; checkpointing local por jurisdicción (`clima_checkpoint_<corte>.json`) para garantizar persistencia incremental ante límites de tasa HTTP 429 de Open-Meteo ERA5.
- `src/etl/fetch_energia_sadi.py`: cálculo e integración nativa de `sadi_diversidad_tech` desde el dataset oficial de centrales CAMMESA (con asignación estricta de 0 tecnologías en Tierra del Fuego como red aislada), incorporando la variable a `data/02_interim/dim_energia_sadi.csv`.
- `src/etl/build_master_table.py`: incorporación formal de `sadi_diversidad_tech` en la *Sección 1 — Energía y Red SADI*, garantizando la preservación determinística de las 63 columnas canónicas en `data/03_processed/master_24_jurisdicciones.parquet` sin requerir parches posteriores.
- `src/gis/fetch_conectividad.py` & `src/etl/fetch_talento_riesgo.py`: mecanismos robustos de reintento y fallback a snapshots existentes en caso de fallos de conexión o indisponibilidad temporal en los servidores de ENACOM, CEP XXI e INPRES.
- `config/data_sources.yaml`: auditoría y actualización de metadatos de fuentes, registrando los cortes verificados (ENACOM 2026-T2, CAMMESA snapshot activo 2026 y CEP XXI formalmente congelado en 2023-11-01 como `STATIC_VERIFIED` sin inventar datos).

### QA & Validation
- `src/etl/validate_master.py`: **PASS** (24 filas × 63 columnas, 0 errores, 0 advertencias, tipos correctos y 100% IDs INDEC verificados).
- `src/modeling/validate_mcda.py`: **PASS** (7/7 pruebas aprobadas: exclusión de 13 NaNs, 16 features normalizadas en $[0, 100]$, restricción física TDF = 0.0 MW / 0 tech SADI, tolerancia de pesos $10^{-6}$, 6 sub-scores acotados y rankings $1 \dots 24$ sin empates).
- `src/modeling/validate_fase3.py`: **PASS** (Clustering $k=4$ Silhouette 0.4641, Monte Carlo 1.000 iteraciones y Modelo Estrella pbi_ready validado con radar en 144 filas y 474 centrales SADI dentro de BBOX Argentina).
- `python -m py_compile app/main.py`: **PASS** (compilación limpia).
- **Hito:** Cierre formal de la **Iteración 2 — Bloque 2B (Pipeline de Actualización Continua Automatizada CI/CD, Auditoría Post-2024 y Frescura de Datos)**.

---

## [2.0.0-alpha.1] — 2026-11-21 | Científico de Datos

### Added
- `docs/metodologia_tier.md`: marco metodológico formal que desglosa el estándar de Uptime Institute (Tier I a IV) e introduce la dimensión estructural de **Aptitud Territorial Tier (Tier-Readiness)**. Define los 4 pilares auditados sin inventar datos: redundancia eléctrica territorial (nodos de generación y diversidad tecnológica CAMMESA, con 0.0 SADI en TDF), estabilidad sísmica de sitio (INPRES-CIRSOC 103), resiliencia térmica estival (temperatura máxima ERA5) y madurez de red/fibra (ENACOM). Incluye justificación de colinealidad controlada ($r < 0.70$ con todas las dimensiones).
- `docs/resultados_tier_v2.md`: auditoría comparativa rigurosa del Top 10 de las 24 jurisdicciones entre la versión `v1.0.0` (5 dimensiones) y la versión `v2.0.0-alpha.1` (6 dimensiones), explicando los movimientos clave (ej. salto de Buenos Aires de #9 a #4 en Campus IA gracias a su máximo Tier-Readiness de 72.35 pts; ascenso de Córdoba de #7 a #5; caída de San Juan de #10 a #11 por sismicidad Zona 4; solidez de Santa Cruz y Chubut en los puestos #1 y #2; y liderazgo indiscutido de CABA en Nodos Edge con 75.16 pts).
- Derivación oficial de `sadi_diversidad_tech` en `data/03_processed/master_24_jurisdicciones.parquet` (63 columnas, validado al 100% con `src/etl/validate_master.py` sin nulos ni errores).

### Changed
- `src/modeling/preprocessing.py`: incorporadas 2 nuevas features operativas de soporte Tier-Readiness (`norm_n_centrales_sadi` con `log1p` y `norm_sadi_diversidad_tech`), elevando el total a 16 features normalizadas en $[0, 100]$. Tratamiento robusto con fallback automático para derivar diversidad tecnológica desde `geo_centrales_sadi.csv` en caso de tablas desactualizadas.
- `src/modeling/mcda_engine.py`: ampliado el motor MCDA a **6 sub-scores dimensionales** (`subscore_tier_readiness` integrado con pesos intra-dimensión auditados que suman exactamente 1.0). Incorporado mecanismo de desempate en ranking evaluando score continuo antes de truncamiento a 4 decimales para garantizar permutación perfecta $1 \dots 24$.
- `config/weights_profiles.json`: recalibrados los 3 perfiles analíticos a 6 dimensiones con suma exacta igual a `1.0` (tolerancia estricta $10^{-6}$):
  - `campus_ia_training`: Energía 0.30, Clima 0.20, Tier-Readiness 0.15, Fiscal 0.15, Conectividad 0.10, Talento/Riesgo 0.10.
  - `nodo_inferencia_edge`: Conectividad 0.30, Talento/Riesgo 0.20, Tier-Readiness 0.15, Energía 0.15, Fiscal 0.10, Clima 0.10.
  - `benchmark_cabase`: Equiponderado en 6 dimensiones ($1/6$ cada una = 0.166667 / 0.166666).
- `src/modeling/clustering.py`: actualizado para entrenar K-Means sobre el vector de 6 dimensiones. Evaluación de $k \in [3, 6]$ confirma $k=4$ óptimo (Silhouette 0.4641, inercia 18.077,6), preservando los 4 arquetipos ejecutivos (`Hub Metropolitano`, `Polo Austral`, `Corredor Energético`, `Brecha Fiscal/Infraestructura`).
- `src/modeling/montecarlo.py`: adaptado para simular vectorizadamente perturbaciones estocásticas ($\pm 20\%$) sobre las 6 dimensiones con 1.000 iteraciones (`seed=42`).
- `src/modeling/export_bi_feeds.py`: ampliado `DIMENSION_DISPLAY_NAMES` con `"subscore_tier_readiness": "Aptitud Territorial Tier (Tier-Readiness)"`. Regenerada la tabla `data/04_outputs/pbi_ready/fact_subscores_radar.csv` con exactamente **144 filas** ($24 \text{ jurisdicciones} \times 6 \text{ dimensiones}$).
- `docs/data_dictionary.md`: actualizado incorporando `n_centrales_sadi` y `sadi_diversidad_tech` en la Sección 1.

### QA & Validation
- `src/etl/validate_master.py`: **PASS** (24 filas, 63 columnas, 0 errores, 0 advertencias).
- `src/modeling/validate_mcda.py`: **PASS** (7/7 pruebas aprobadas: exclusión de 13 NaNs, 16 features normalizadas, regla física TDF = 0.0 MW y 0 fuentes SADI, tolerancia de pesos $10^{-6}$, 6 sub-scores acotados a $[0, 100]$, contrato Parquet/CSV y rankings $1 \dots 24$ sin empates).
- `src/modeling/validate_fase3.py`: **PASS** (Clustering $k=4$, Monte Carlo 1.000 runs, Modelo Estrella pbi_ready validado con radar en 144 filas y 474 centrales SADI en BBOX argentino).
- `python -m py_compile app/main.py`: **PASS** (compilación limpia).
- **Hito:** Cierre exitoso de la **Iteración 2 — Bloque 2A (Integración Estructural de Tier-Readiness en el Motor MCDA)**.

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
