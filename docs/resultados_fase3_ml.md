# Reporte Analítico — Resultados de Modelado ML, Sensibilidad y Arquetipos (Fase 3)

**Proyecto:** Viabilidad de Data Centers y Campus de Inteligencia Artificial en Argentina  
**Hito:** Bloque 3.2 — Cierre de Fase 3  
**Versión de Entrega:** `v0.7.0`  
**Fecha:** 2026-11-20  
**Rol:** Científico de Datos  

---

## 1. Resumen Ejecutivo

La **Fase 3** concluye con el desarrollo y validación integral de tres capas analíticas avanzadas:
1. **Segmentación No Supervisada (Clustering K-Means):** Identificación de 4 arquetipos provinciales sobre el espacio multidimensional de sub-scores, con justificación matemática mediante Silhouette Score e Inercia.
2. **Análisis de Sensibilidad Estocástica (Simulación Monte Carlo):** 1.000 iteraciones por perfil con perturbación del $\pm 20\%$ en las ponderaciones directivas, determinando la robustez de los rankings y probabilidades empíricas de calificar en el Top 3 y Top 5.
3. **Capa de Servicio para Visualización (Modelo Estrella BI & GIS):** Generación de datasets optimizados en `data/04_outputs/pbi_ready/` en formato CSV con BOM (`UTF-8-SIG`), conectando las 24 jurisdicciones con 474 centrales de generación del SADI georreferenciadas en EPSG:4326.

---

## 2. Justificación Matemática y Selección de Clusters ($k=4$)

Se evaluó la estructura topológica del espacio $\mathbb{R}^5$ (sub-scores normalizados de Energía, Clima, Conectividad, Fiscal y Talento) mediante un barrido de particiones $k \in [3, 6]$ con semilla fija `random_state=42`:

| Cantidad de Clusters ($k$) | Silhouette Score | Inercia (Distancia Cuadrática Intra-Cluster) | Diagnóstico e Interpretabilidad de Negocio |
|---|:---:|:---:|---|
| **$k = 3$** | **0.5554** | 22.680,49 | **Sobre-agrupamiento:** Aunque maximiza Silhouette, agrupa a 18 provincias en un solo cluster homogéneo, perdiendo granularidad operativa. |
| **$k = 4$ (Seleccionado)** | **0.4784** | **16.225,63** | **Óptimo de Negocio:** Caída pronunciada de inercia (-28,5%) aislando los 4 perfiles estructurales de infraestructura y regulación en Argentina. |
| **$k = 5$** | 0.3410 | 12.342,80 | **Sub-partición forzada:** Drástica degradación del Silhouette (-28,7%) sin ganar diferenciación estratégica clara. |
| **$k = 6$** | 0.3335 | 8.850,19 | **Sobre-segmentación:** Clusters residuales con solapamiento en distancias relativas. |

### Taxonomía de los 4 Arquetipos de Infraestructura Descubiertos

| Cluster ID | Arquetipo de Infraestructura | Provincias Miembros | Centroide Diagnóstico ($\bar{x}$) | Rol Estratégico en Ecosistema de Datos / IA |
|:---:|---|---|---|---|
| **1** | **Hub Metropolitano & Conectividad Core** | CABA, Buenos Aires *(2 jurisdicciones)* | Conectividad: **83.4**<br>Talento STEM: **78.9**<br>Fiscal: **80.8**<br>Energía: **59.1**<br>Clima: **28.3** | **Dominio en Perfil B (Inferencia Edge):** Concentración crítica de fibra troncal, cercanía al amarre submarino (Las Toninas) y máxima oferta de talento IT. |
| **2** | **Polo Austral & Free-Cooling Extremo** | Santa Cruz, Tierra del Fuego *(2 jurisdicciones)* | Clima: **92.5**<br>Fiscal: **65.3**<br>Energía: **39.0**<br>Conectividad: **24.4**<br>Talento STEM: **22.3** | **Ventaja Térmica para Perfil A (Campus IA):** Eficiencia climática insuperable para *free-cooling* continuo (PUE < 1.15). Requiere resolver redundancia eléctrica y conectividad satelital/terrestre. |
| **3** | **Corredor Productivo & Energético SADI/Renovable** | Córdoba, Mendoza, Neuquén, Río Negro, Chubut, San Juan, Salta, Santa Fe, Entre Ríos, Catamarca, Corrientes, Chaco, Jujuy, Misiones, San Luis, Tucumán *(16 jurisdicciones)* | Fiscal: **100.0**<br>Energía: **53.0**<br>Conectividad: **47.2**<br>Talento STEM: **35.6**<br>Clima: **22.0** | **Base Territorial RIGI:** Adhesión normativa plena al RIGI e incentivos a la economía del conocimiento, alta potencia instalada en generación hidro/renovable y balance intermedio. |
| **4** | **Brecha Fiscal e Infraestructura Rezagada** | Formosa, La Pampa, La Rioja, Santiago del Estero *(4 jurisdicciones)* | Fiscal: **2.1**<br>Energía: **45.4**<br>Conectividad: **36.0**<br>Talento STEM: **29.4**<br>Clima: **12.4** | **Baja Competitividad Inmediata:** Desventaja regulatoria severa (no adhesión a RIGI o alícuotas elevadas), clima caluroso y déficit en infraestructura de telecomunicaciones. |

---

## 3. Simulación de Sensibilidad Monte Carlo (1.000 Runs)

Para evaluar si los rankings obtenidos en el modelo MCDA determinístico eran artefactos de las ponderaciones o decisiones estructurales robustas, se perturbaron los pesos de los Perfiles A y B en $\pm 20\%$ con renormalización a $\sum w_i = 1.0$:

### Perfil A — Campus de Entrenamiento IA (Alta Densidad)

| Jurisdicción | Score Base | Score Medio (MC) | Desv. Est. ($\sigma$) | Intervalo P5–P95 | Rank Mediano | Prob. Top 3 (%) | Prob. Top 5 (%) | Diagnóstico de Estabilidad |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Santa Cruz** | **67.00** | **66.99** | 0.89 | [65.47, 68.41] | **1** | **100.0%** | **100.0%** | **Ultra-robusta (#1 Absoluto):** El clima frío y la potencia instalada la blindan ante variaciones de ponderación. |
| **Chubut** | **64.87** | **64.86** | 1.14 | [62.99, 66.63] | **2** | **100.0%** | **100.0%** | **Ultra-robusta (#2 Consolidado):** Fuerte balance eólico, clima favorable y adhesión RIGI. |
| **CABA** | **64.36** | **64.36** | 1.49 | [61.93, 66.85] | **3** | **100.0%** | **100.0%** | **Ultra-robusta (#3 Consolidado):** Su altísima conectividad y marco regulatorio compensan el clima cálido. |
| **Buenos Aires** | 58.74 | 58.74 | 1.34 | [56.49, 60.91] | 4 | 0.0% | 99.4% | **Top 5 Sólido (#4):** Consistencia del 99.4% en Top 5, pero sin superar a CABA ni Patagonia Austral. |
| **Córdoba** | 56.47 | 56.46 | 1.38 | [54.14, 58.67] | 5 | 0.0% | 0.6% | **Disputada (#5):** Quinta posición determinística, pero compite estrechamente con Neuquén y Mendoza. |

### Perfil B — Nodos de Inferencia / Edge (Baja Latencia)

| Jurisdicción | Score Base | Score Medio (MC) | Desv. Est. ($\sigma$) | Intervalo P5–P95 | Rank Mediano | Prob. Top 3 (%) | Prob. Top 5 (%) | Diagnóstico de Estabilidad |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **CABA** | **81.58** | **81.58** | 1.00 | [79.88, 83.16] | **1** | **100.0%** | **100.0%** | **Líder Invariable (#1 Indiscutido):** Score superior a 80 puntos; 100% de victorias en simulaciones. |
| **Buenos Aires** | **63.89** | **63.87** | 0.77 | [62.64, 65.15] | **2** | **100.0%** | **100.0%** | **Ultra-robusta (#2):** Baja dispersión ($\sigma = 0.77$) por cercanía física directa al cable submarino. |
| **Córdoba** | **59.17** | **59.17** | 0.83 | [57.83, 60.59] | **3** | **100.0%** | **100.0%** | **Ultra-robusta (#3):** Polo tecnológico mediterráneo, alta densidad de graduados STEM e IXP central. |
| **Santa Fe** | 54.34 | 54.34 | 0.84 | [52.93, 55.70] | 4 | 0.0% | 99.9% | **Top 5 Seguro (#4):** Excelente capilaridad de red y cercanía geográfica a la red troncal. |
| **San Luis** | 51.52 | 51.52 | 1.02 | [49.83, 53.20] | 5 | 0.0% | 95.8% | **Top 5 Sólido (#5):** Tradición de infraestructura digital provincial y régimen fiscal favorable. |

---

## 4. Estructura y Validación del Modelo Estrella BI (`pbi_ready/`)

Se consolidaron 4 tablas relacionales limpias bajo codificación `utf-8-sig` (compatible de forma nativa con Power BI Desktop y Streamlit sin errores de codificación ni requerir transformaciones complejas en DAX):

1. **`dim_jurisdicciones.csv` (24 filas × 9 columnas):**
   - Clave Primaria: `jurisdiccion_id` (código INDEC de 2 dígitos).
   - Atributos geográficos: `lat_capital`, `lon_capital`, `region_argentina`.
   - Atributos de clustering: `cluster_id` (1 a 4), `cluster_nombre` y `cluster_descripcion`.
2. **`fact_scores_perfiles.csv` (72 filas × 15 columnas):**
   - Formato largo de las 24 provincias cruzadas contra los 3 perfiles (`campus_ia_training`, `nodo_inferencia_edge`, `benchmark_cabase`).
   - Métricas: `score_base`, `rank_base`, `mc_score_mean`, `mc_score_std`, `mc_score_p5`, `mc_score_p95`, `mc_rank_median`, `prob_top3_pct`, `prob_top5_pct`.
3. **`fact_subscores_radar.csv` (120 filas × 5 columnas):**
   - 24 provincias $\times$ 5 sub-scores dimensionales [0, 100] formateados para gráficos radiales / Spider charts.
4. **`geo_centrales_sadi.csv` (474 filas × 11 columnas):**
   - 474 centrales de generación registradas en CAMMESA con coordenadas en EPSG:4326.
   - 100% de coordenadas validadas dentro del Bounding Box de Argentina (Lat $[-56.0, -21.0]$, Lon $[-74.0, -53.0]$), 0 coordenadas nulas y 0 en $(0,0)$.
   - 23 jurisdicciones representadas (Tierra del Fuego debidamente identificada con 0 centrales SADI por su condición física de red eléctrica aislada).

---

## 5. Conclusiones y Próximos Pasos (Fase 4)

- **Desacoplamiento Total:** Toda la inteligencia matemática (MCDA, K-Means y Monte Carlo) quedó encapsulada y precomputada en `src/modeling/` y `data/04_outputs/`.
- **Preparación para la Fase 4 (Streamlit & Dashboards):**
  - Los feeds en `pbi_ready/` alimentarán directamente el dashboard ejecutivo de Streamlit y el archivo Power BI `.pbix`.
  - La capa geoespacial `geo_centrales_sadi.csv` permitirá superponer la infraestructura energética real sobre el mapa coroplético de viabilidad provincial.
