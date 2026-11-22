# Metodología de Proyección Prospectiva y Análisis de Escenarios (2026–2036)
## Plataforma de Viabilidad para Data Centers y Campus de IA en Argentina

**Autor:** Equipo de Ciencia de Datos & Modelado Espacial  
**Fecha de corte:** Noviembre 2026  
**Versión metodológica:** 2.0.0 (Bloque 2C)  
**Clasificación:** Marco Teórico, Ecuaciones de Estado y Contrato de Proyección  

---

## 1. Introducción y Propósito

El planeamiento de infraestructura crítica digital —en particular **Campus de Entrenamiento de Inteligencia Artificial (Alta Densidad)** y **Nodos de Inferencia / Edge**— demanda horizontes de inversión de capital (CAPEX) de 5 a 15 años. Una fotografía estática del año base subestima los cambios tecnológicos acelerados (despliegue de fibra óptica, curvas de penetración de FTTH), las transiciones en la matriz de generación eléctrica (expansión eólica y solar) y los vectores de cambio global (calentamiento térmico observado y su impacto en el PUE de refrigeración).

Este documento establece la metodología matemática, estadística y física para proyectar el desempeño de las **24 jurisdicciones de Argentina** en 7 puntos temporales discretos a lo largo de una década:
- **Año Base:** 2026 ($t=0$).
- **Corto Plazo (+2 años):** 2028.
- **Intermedio (+4 años):** 2030.
- **Medio Plazo (+5 años):** 2031.
- **Intermedio (+6 años):** 2032.
- **Intermedio (+8 años):** 2034.
- **Largo Plazo (+10 años):** 2036.

Se definen **tres escenarios estructurales y regulatorios:**
1. **Acelerado (Inversión RIGI, Desregulación & Expansión Renovable):** Alta tracción de inversiones extranjeras, adhesión plena al RIGI, finalización ágil de proyectos en cartera, habilitación de microrredes off-grid y rápida saturación de fibra óptica.
2. **Tendencial (Inercial / Histórico):** Continuidad del ritmo de inversión observado 2015–2024, culminación gradual de obras en construcción, crecimiento orgánico de conectividad y calentamiento inercial según tendencias históricas de ERA5.
3. **Conservador (Restricciones Macroeconómicas & Brechas de Infraestructura):** Escasez de financiamiento, parálisis de proyectos no iniciados, atraso tarifario, mantenimiento de cuellos de botella en transporte eléctrico y estancamiento de conectividad y capital humano.

---

## 2. Principios Innegociables de Rigor Físico y Matemático

Siguiendo el mandato de gobernanza establecido en `AGENTS.md`:

### 2.1 Cero Datos Inventados
No se crean datos sintéticos haciéndolos pasar por mediciones oficiales. Toda proyección se ancla en:
- La tabla maestra consolidada (`master_24_jurisdicciones.parquet`).
- La cartera oficial de proyectos del Registro Nacional RenovAr / MATER (`minem_renovar_mater_raw.csv`, 180 registros, ~2.228,5 MW totales y 1.852,7 MW en construcción).
- La serie histórica diaria climática 2000–2023 de Open-Meteo ERA5 (`clima_24_jurisdicciones_raw.json`).
- Estadísticas del ENACOM y del CEP XXI.

### 2.2 Anclaje de Normalización al Año Base (Fixed Base Scaling)
Para que el análisis prospectivo mida **progreso real en infraestructura y aptitud** (y no meros desplazamientos relativos del ranking), las variables proyectadas se transforman utilizando los límites empíricos fijos $[x_{\min}^{2026}, x_{\max}^{2026}]$ del año base 2026:

$$x_{\text{norm}}(t) = \text{clip}\left(\frac{x(t) - x_{\min}^{2026}}{x_{\max}^{2026} - x_{\min}^{2026}} \times 100,\ 0.0,\ 100.0\right) \quad \text{(para maximizar)}$$

$$x_{\text{norm}}(t) = \text{clip}\left(\frac{x_{\max}^{2026} - x(t)}{x_{\max}^{2026} - x_{\min}^{2026}} \times 100,\ 0.0,\ 100.0\right) \quad \text{(para minimizar)}$$

Cualquier valor que supere los límites del año 2026 se recorta a 100.0 (o 0.0), preservando la comparabilidad intertemporal y garantizando que:
$$\Delta\text{Score}_{vs\_2026}(t) = \text{Score}(t) - \text{Score}(2026)$$
refleje ganancias o pérdidas absolutas de capacidad.

### 2.3 Origen Único en Año Base ($t = 2026$)
En el año base 2026, los tres escenarios deben confluir exactamente en el punto de partida observado:
$$\text{Score}_{\text{Acelerado}}(2026) = \text{Score}_{\text{Tendencial}}(2026) = \text{Score}_{\text{Conservador}}(2026) = \text{Score}_{\text{MCDA\_Base}}$$
$$\Delta\text{Score}_{vs\_2026}(2026) = 0.0000 \quad \forall \text{ jurisdicción, escenario y perfil.}$$

---

## 3. Dinámica Sectorial por Dimensión

### 3.1 Dimensión 1: Energía y Expansión Renovable

#### Cartera Real RenovAr / MATER
La cartera con potencia oficial registrada en `minem_renovar_mater_raw.csv` comprende:
- **En Construcción:** 1.852,7 MW distribuidos en Santa Cruz (1.310,0 MW eólico/hidro), Corrientes (282,9 MW biomasa), La Rioja (100,0 MW solar), San Juan (76,5 MW solar), La Pampa (60,0 MW), Catamarca (49,5 MW), Tucumán (45,0 MW), Córdoba (12,2 MW), Mendoza (10,0 MW), Santa Fe (3,1 MW), Buenos Aires (1,5 MW) y San Luis (2,0 MW).
- **No iniciado:** 171,6 MW (Buenos Aires 64,5 MW, Santa Cruz 37,9 MW, La Pampa 25,8 MW, Córdoba 12,9 MW, Chaco 10,0 MW, San Luis 10,0 MW, Santa Fe 10,0 MW, Mendoza 0,5 MW).

#### Tasa de Ejecución y Expansión SADI por Escenario
Para cada jurisdicción $i$ en el año $t \ge 2026$:
$$P_i(t) = P_{i, \text{SADI}}^{2026} \times (1 + g_{\text{macro}})^{\Delta t} + \gamma_{\text{const}}(t) \cdot P_{i, \text{const}} + \gamma_{\text{no\_iniciado}}(t) \cdot P_{i, \text{no\_iniciado}}$$

Parámetros por escenario:
| Parámetro | Acelerado | Tendencial | Conservador |
|---|:---:|:---:|:---:|
| $g_{\text{macro}}$ (expansión anual de fondo) | $+3.5\%$ anual | $+1.5\%$ anual | $+0.5\%$ anual |
| $\gamma_{\text{const}}(2028)$ (avance en const.) | $100\%$ | $60\%$ | $30\%$ |
| $\gamma_{\text{const}}(2031)$ (avance en const.) | $100\%$ | $100\%$ | $50\%$ |
| $\gamma_{\text{const}}(2036)$ (avance en const.) | $100\%$ | $100\%$ | $70\%$ |
| $\gamma_{\text{no\_iniciado}}(2028)$ | $30\%$ | $0\%$ | $0\%$ |
| $\gamma_{\text{no\_iniciado}}(2031)$ | $80\%$ | $25\%$ | $0\%$ |
| $\gamma_{\text{no\_iniciado}}(2036)$ | $100\%$ | $40\%$ | $10\%$ |

#### Regla Física de Tierra del Fuego
- En 2026, 2028, 2030, y en **todos los años de los escenarios Tendencial y Conservador**, la potencia SADI de Tierra del Fuego es estrictamente **0.0 MW** (isla no interconectada físicamente al Sistema Argentino de Interconexión).
- En el escenario **Acelerado**, a partir de **2031 (+5 años)**, se habilita un supuesto explícito y transparente de microrred off-grid eólica dedicada a computación de alto rendimiento en Río Grande (50 MW en 2031, 100 MW en 2034, 150 MW en 2036). Se documenta con claridad que este insumo computa como capacidad efectiva disponible para Data Centers sin falsear las estadísticas oficiales del SADI continental.

#### Participación Renovable ($PctRenovable$)
La matriz renovable provincial avanza impulsada por los nuevos parques eólicos y solares, acotada al $100\%$:
$$PctRenov_i(t) = \min\left(100.0,\ PctRenov_i^{2026} + \Delta Renov_i(t)\right)$$

---

### 3.2 Dimensión 2: Clima, Calentamiento Observado y Deterioro de PUE

#### Pendientes Empíricas ERA5 (2000–2023)
A partir de la regresión por mínimos cuadrados ordinarios (OLS) sobre la serie diaria de `clima_24_jurisdicciones_raw.json` para cada capital de provincia:
$$\text{TemperaturaMedia}(y) = \alpha_{prov} + \beta_{prov} \cdot y + \epsilon$$

Valores empíricos observados por provincia ($\beta_{prov}$ en °C/año):
- **Calentamiento Severo (> 0.07 °C/año):** La Rioja (+0.120), Catamarca (+0.096), San Juan (+0.080), Mendoza (+0.076), Tucumán (+0.074).
- **Calentamiento Moderado (0.03 a 0.07 °C/año):** Tierra del Fuego (+0.065), San Luis (+0.055), Córdoba (+0.053), Entre Ríos (+0.040), Santa Cruz (+0.040), Chaco (+0.039), Jujuy (+0.034), Santa Fe (+0.033), CABA (+0.031).
- **Calentamiento Leve / Estable (< 0.03 °C/año):** Corrientes (+0.026), Misiones (+0.024), Buenos Aires (+0.024), Formosa (+0.023), Santiago del Estero (+0.022), Chubut (+0.019), Río Negro (+0.012), La Pampa (+0.008), Neuquén (+0.000 / piso neutro), Salta (+0.000 / piso neutro).

Media nacional de calentamiento: **$+0.0406\ ^\circ\text{C}/\text{año}$** ($+0.41\ ^\circ\text{C}/\text{década}$).

#### Modelado del PUE Climatológico y Horas de Free Cooling
Para cada año $t$, la anomalía térmica acumulada es:
$$\Delta T_i(t) = \max(0.0,\ \beta_{i, prov}) \cdot (t - 2026) \cdot \lambda_{\text{clima}}$$

Donde $\lambda_{\text{clima}}$ modula la trayectoria climática global:
- $\lambda_{\text{clima}} = 1.00$ en Tendencial (continuidad de la tasa histórica observada).
- $\lambda_{\text{clima}} = 1.25$ en Conservador (mayor estrés térmico / forzamiento radiativo alto sin mitigación).
- $\lambda_{\text{clima}} = 0.85$ en Acelerado (trayectoria con mitigación y tecnologías de enfriamiento de alta eficiencia).

El incremento de temperatura ambiental reduce la ventana de horas en las que $T_{\text{ext}} < 18\ ^\circ\text{C}$, provocando un incremento del PUE:
$$\Delta PUE_i(t) = \Delta T_i(t) \times \kappa_{PUE} \quad (\kappa_{PUE} \approx 0.0045\ \text{PUE}/^\circ\text{C})$$
$$PUE_i(t) = \text{clip}\left(PUE_i^{2026} + \Delta PUE_i(t),\ 1.10,\ PUE_{\text{base\_mecanico}} = 1.58\right)$$

Este modelo penaliza el subscore de clima a lo largo de la década en zonas cálidas, consolidando la ventaja comparativa estructural de la Patagonia Austral.

---

### 3.3 Dimensión 3: Conectividad y Curvas Logísticas de Saturación

#### Ecuación Sigmoidea de Adopción (FTTH y Penetración)
La sustitución de cobre/coaxial por fibra óptica (FTTH) no sigue una trayectoria lineal infinita, sino una curva logística con rendimientos decrecientes y saturación física hacia un techo asintótico provincial $L$:

$$S_i(t) = \frac{L_i}{1 + \left(\frac{L_i - S_i(2026)}{S_i(2026)}\right) e^{-k_{\text{escenario}} \cdot (t - 2026)}}$$

Parámetros:
- **Techo provincial $L_i$:** $L_i = \min(100.0,\ \max(S_i(2026) + 15.0,\ 92.0\%))$ en Acelerado; $85.0\%$ en Tendencial; $75.0\%$ en Conservador.
- **Velocidad de adopción $k_{\text{escenario}}$:** $k_{\text{acelerado}} = 0.25$, $k_{\text{tendencial}} = 0.15$, $k_{\text{conservador}} = 0.07$.

#### Velocidad Media de Bajada (Mbps)
Sigue una curva de avance tecnológico cóncava acotada hacia techos según la infraestructura de backhaul disponible:
$$V_i(t) = \min\left(V_{\text{techo}},\ V_i(2026) \cdot (1 + \mu_{\text{escenario}})^{t - 2026}\right)$$
- Acelerado: $\mu = 14\%$ anual, $V_{\text{techo}} = 1.000\ \text{Mbps}$.
- Tendencial: $\mu = 8\%$ anual, $V_{\text{techo}} = 500\ \text{Mbps}$.
- Conservador: $\mu = 3\%$ anual, $V_{\text{techo}} = 250\ \text{Mbps}$.

#### Distancia a Cables Submarinos (Las Toninas)
Permanece **estrictamente invariante** a lo largo de todo el horizonte temporal: la distancia geográfica euclidiana/terrestre no se altera con el paso de los años.

---

### 3.4 Dimensión 4: Marco Fiscal y Regulatorio

- **Adhesión al RIGI:**
  - En el año base 2026, 14 jurisdicciones están adheridas.
  - *Acelerado:* Adhesión progresiva del resto de las jurisdicciones (Santa Fe y CABA hacia 2028; Buenos Aires hacia 2030; 100% de adhesión para 2031).
  - *Tendencial:* Se mantienen las 14 jurisdicciones adheridas en 2026, sin nuevas sanción de leyes provinciales.
  - *Conservador:* Estancamiento regulatorio e incertidumbre jurídica.
- **Alícuota IIBB Actividades TIC y Promoción Fiscal:**
  - *Acelerado:* Reducción paulatina de alícuotas IIBB tech hacia techos de $1.5\% - 0.0\%$ en provincias con polos tecnológicos activos.
  - *Tendencial:* Mantenimiento de alícuotas actuales.
  - *Conservador:* Presión fiscal inercial o incremento de alícuotas efectivas.

---

### 3.5 Dimensión 5: Talento STEM y Riesgo Físico

- **Seguridad Sísmica (INPRES-CIRSOC 103):** Estrictamente **invariante**. La zonificación geotécnica (Zonas 0 a 4) no cambia en una escala decenal.
- **Densidad STEM y Empleo en Software (CLAE 62):**
  - Crecimiento orgánico derivado de programas universitarios y academias tecnológicas:
    - *Acelerado:* $+5.0\%$ anual acumulado en puestos software, saturando hacia mayores densidades.
    - *Tendencial:* $+2.0\%$ anual acumulado.
    - *Conservador:* $+0.0\%$ anual (crecimiento absorbido por emigración o estancamiento del sector).

---

### 3.6 Dimensión 6: Aptitud Territorial Tier (Tier-Readiness)

Calculada de forma integrada a partir de:
- Número de centrales eléctricas y diversidad tecnológica CAMMESA (aumenta según entrada de nuevos proyectos RenovAr).
- Madurez de la red troncal de fibra óptica y velocidad.
- Resiliencia sísmica (fija) y estrés térmico estival.

---

## 4. Orquestación del Scoring Compuesto (WSM)

Para cada jurisdicción $i$, año $t \in [2026, 2028, 2030, 2031, 2032, 2034, 2036]$ y escenario $s \in [\text{Acelerado}, \text{Tendencial}, \text{Conservador}]$:

1. Se proyectan las 16 features operativas primarias.
2. Se normalizan aplicando los **límites fijos de 2026** y recorte en $[0, 100]$.
3. Se calculan los 6 sub-scores dimensionales aplicando los pesos intra-dimensión de `INTRA_DIMENSION_WEIGHTS`.
4. Se calcula el **Score Compuesto Final** invocando directamente `calculate_composite_score(df_subscores, weights)` de `src/modeling/mcda_engine.py` para los 3 perfiles oficiales:
   - `campus_ia_training`
   - `nodo_inferencia_edge`
   - `benchmark_cabase`
5. Se calculan los rankings ordinales ($1 \dots 24$) en cada corte temporal, resolviendo empates mediante precisión continua.

---

## 5. Medición de Incertidumbre y Sensibilidad

Para cada combinación de jurisdicción, año y perfil se computan:
- **Banda de Sensibilidad:**
  - Cota Inferior ($p10$): Escenario Conservador.
  - Valor Central Esperado ($p50$): Escenario Tendencial.
  - Cota Superior ($p90$): Escenario Acelerado.
- **Deltas respecto al Origen 2026:**
  $$\Delta\text{Score}_{vs\_2026} = \text{Score}_i(t, s) - \text{Score}_i(2026, s)$$
  $$\Delta\text{Rank}_{vs\_2026} = \text{Rank}_i(2026, s) - \text{Rank}_i(t, s)$$
  *(un valor positivo en $\Delta\text{Rank}$ indica ganancia neta de posiciones en el ranking).*

---

## 6. Estructura de Salida y Contratos de Datos

### 6.1 `data/04_outputs/proyecciones_2026_2036.parquet` y `.csv`
Tabla completa en formato granular con 504 filas ($24 \text{ jurisdicciones} \times 7 \text{ años} \times 3 \text{ escenarios}$) y columnas:
- Identificadores y geografía: `jurisdiccion_id`, `jurisdiccion_nombre`, `jurisdiccion_corta`, `region_argentina`.
- Temporalidad y escenario: `anio`, `horizonte`, `escenario_id`, `escenario_nombre`.
- Sub-scores dimensionales: `subscore_energia`, `subscore_clima`, `subscore_conectividad`, `subscore_fiscal`, `subscore_talento_riesgo`, `subscore_tier_readiness`.
- Scores y Rankings por perfil:
  - `score_campus_ia_training`, `rank_campus_ia_training`, `delta_score_campus_ia`, `delta_rank_campus_ia`.
  - `score_nodo_inferencia_edge`, `rank_nodo_inferencia_edge`, `delta_score_nodo_edge`, `delta_rank_nodo_edge`.
  - `score_benchmark_cabase`, `rank_benchmark_cabase`, `delta_score_cabase`, `delta_rank_cabase`.

### 6.2 `data/04_outputs/pbi_ready/fact_proyecciones_2026_2036.csv`
Tabla de hechos del modelo estrella para Power BI (UTF-8 con BOM), con clave externa `jurisdiccion_id` conectable a `dim_jurisdicciones.csv`, enriquecida para permitir análisis longitudinales, gráficos de cinta (*bump charts*) y segmentación interactiva por escenario y perfil.
