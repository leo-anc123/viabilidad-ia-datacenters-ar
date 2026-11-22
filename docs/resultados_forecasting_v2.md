# Reporte de Resultados: Análisis Predictivo Prospectivo (2026–2036)
## Dinámica Intertemporal de Viabilidad para Data Centers y Campus de IA en las 24 Jurisdicciones

**Autor:** Equipo de Ciencia de Datos & Modelado Espacial  
**Fecha de corte:** Noviembre 2026  
**Versión de análisis:** `v2.0.0-alpha.3` (Bloque 2C)  
**Dataset de salida:** `data/04_outputs/proyecciones_2026_2036.parquet` y `data/04_outputs/pbi_ready/fact_proyecciones_2026_2036.csv`

---

## 1. Resumen Ejecutivo y Hallazgos Principales

El modelado prospectivo decenal (horizontes 2026, 2028, 2030, 2031, 2032, 2034 y 2036 bajo tres escenarios macroeconómicos y regulatorios: **Acelerado**, **Tendencial** y **Conservador**) revela transformaciones críticas en el mapa de competitividad argentino para la radicación de infraestructura de computación intensiva:

1. **Hegemonía y Consolidación de la Patagonia Austral (Santa Cruz y Chubut):**
   - En el **Perfil A (Campus de Entrenamiento IA)**, **Santa Cruz** consolida su puesto **#1 indiscutido**, escalando en el escenario Tendencial de **64.09 pts** en 2026 a **70.80 pts** en 2036 (+6.71 pts netos). Este liderazgo se apoya en el ingreso de los 1.310 MW de la cartera RenovAr en construcción y una resiliencia climática insuperable (calentamiento proyectado inferior a la media y PUE de diseño de 1.15).
   - **Chubut** afianza el puesto **#2**, incrementando su score de **63.57 pts** a **67.09 pts** en 2036.
2. **El "Desbloqueo" Condicionado de Tierra del Fuego:**
   - En los escenarios **Tendencial y Conservador**, Tierra del Fuego permanece en el pelotón bajo (**puesto #20–#21**, ~36 a 40 pts) debido a la restricción física ineludible de aislamiento del SADI (0.0 MW).
   - En el escenario **Acelerado**, el despliegue documentado de una microrred eólica off-grid dedicada a cómputo de alto rendimiento a partir de 2031 (50 MW escalando a 150 MW en 2036) desata el máximo potencial de su clima frío (PUE 1.15, score clima 100.0), protagonizando el **mayor salto intertemporal del país (+17 posiciones)**, pasando del puesto **#19** en 2026 al puesto **#4 en 2031 (64.93 pts)** y alcanzando el **puesto #2 nacional en 2036 (70.75 pts)**.
3. **El Gran Ascenso del Litoral Energético (Corrientes):**
   - **Corrientes** es el mayor ganador orgánico en el escenario Tendencial: trepa del puesto **#15** en 2026 al puesto **#7** en 2036 (+8 puestos netos, +11.74 pts de score compuesto en Campus IA), impulsado por la puesta en marcha de 282,9 MW de biomasa y renovables en construcción.
4. **Resiliencia de los Hubs Urbanos en Inferencia (CABA y Buenos Aires):**
   - En el **Perfil B (Nodos de Inferencia / Edge)**, **CABA** retiene el puesto **#1 nacional** en los tres escenarios hacia 2036 (escalando de 75.16 pts a 78.28 pts en Acelerado), respaldada por su insuperable densidad de talento y latencia a Las Toninas.
   - Sin embargo, las provincias de **Córdoba**, **Santa Fe** y **Mendoza** aceleran su convergencia en inferencia gracias a la saturación logística de fibra FTTH (>85% de hogares), reduciendo la brecha relativa con el Área Metropolitana.
5. **Estrés Térmico y Riesgo de Competitividad en el Norte Grande:**
   - Jurisdicciones con pendientes de calentamiento estival severas observadas en ERA5 (>0.07 °C/año, ej. La Rioja, Catamarca, San Juan, Tucumán) experimentan una reducción en sus horas de *free cooling* y un deterioro gradual del PUE. Aquellas que no compensan esta penalización con grandes carteras de generación pierden entre 4 y 6 posiciones relativas en Campus IA.

---

## 2. Evolución Longitudinal del Ranking: Perfil A (Campus IA Training)

### Tabla 1: Top 10 Jurisdicciones en Escenario TENDENCIAL (2026 vs 2028 vs 2031 vs 2036)

| Jurisdicción | Rank 2026 | Score 2026 | Rank 2028 | Score 2028 | Rank 2031 | Score 2031 | Rank 2036 | Score 2036 | $\Delta\text{Score}$ | $\Delta\text{Rank}$ | Arquetipo |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Santa Cruz** | **1** | 64.09 | **1** | 67.36 | **1** | 69.14 | **1** | **70.80** | **+6.71** | **0** | Polo Austral |
| **Chubut** | **2** | 63.57 | **2** | 64.19 | **2** | 65.55 | **2** | **67.09** | **+3.52** | **0** | Polo Austral |
| **CABA** | **3** | 63.30 | **3** | 63.59 | **3** | 63.99 | **3** | **64.55** | **+1.25** | **0** | Hub Metropolitano |
| **Buenos Aires** | **4** | 59.00 | **4** | 59.33 | **4** | 59.72 | **4** | **60.17** | **+1.17** | **0** | Hub Metropolitano |
| **Río Negro** | **6** | 55.68 | **5** | 56.51 | **5** | 57.84 | **5** | **59.75** | **+4.07** | **+1** | Polo Austral |
| **Córdoba** | **5** | 56.53 | **6** | 56.32 | **6** | 57.60 | **6** | **59.58** | **+3.04** | **-1** | Corredor Energético |
| **Corrientes** | **15** | 47.57 | **9** | 54.75 | **8** | 57.26 | **7** | **59.31** | **+11.74** | **+8** | Corredor Energético |
| **San Luis** | **7** | 55.09 | **7** | 56.10 | **7** | 57.38 | **8** | **57.92** | **+2.82** | **-1** | Corredor Energético |
| **Neuquén** | **8** | 54.78 | **8** | 55.62 | **9** | 57.02 | **9** | **57.87** | **+3.09** | **-1** | Corredor Energético |
| **Santa Fe** | **10** | 53.31 | **11** | 53.94 | **10** | 55.22 | **10** | **57.42** | **+4.11** | **0** | Corredor Energético |

---

## 3. Dinámica Comparativa de Escenarios (Acelerado vs Tendencial vs Conservador)

El contraste entre los tres escenarios estructurales demuestra cómo las políticas de desregulación y de inversión de capital modifican el mapa de viabilidad hacia 2036:

### Gráfico Conceptual de Sensibilidad 2036 (Media Nacional por Perfil)

| Perfil Analítico | Base 2026 | Conservador (2036) | Tendencial (2036) | Acelerado (2036) | Brecha Acel-Cons |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Campus IA Training** | 49.38 pts | 49.52 pts | 54.89 pts | 60.12 pts | **+10.60 pts** |
| **Nodo Inferencia Edge** | 48.97 pts | 50.15 pts | 56.42 pts | 62.88 pts | **+12.73 pts** |
| **Benchmark CABASE** | 46.85 pts | 47.30 pts | 53.22 pts | 59.45 pts | **+12.15 pts** |

### Análisis de Escenarios:
1. **Escenario Acelerado:**
   - La adhesión universal al RIGI y la reducción de alícuotas IIBB eliminan los cuellos de botella fiscales.
   - Tierra del Fuego aprovecha su microrred off-grid y se convierte en el co-líder nacional junto a Santa Cruz.
   - La Pampa experimenta un salto masivo (+14 puestos, del #20 al #6 en Campus IA) gracias al desbloqueo de 85,8 MW de proyectos solares/eólicos y al avance de FTTH.
2. **Escenario Tendencial:**
   - Crecimiento equilibrado centrado en las obras ya en construcción de CAMMESA/RenovAr.
   - Corrientes y Santa Cruz concentran los mayores beneficios netos.
   - CABA y PBA mantienen solidez inercial pero reducen su ventaja ante el fortalecimiento del interior.
3. **Escenario Conservador:**
   - La parálisis de proyectos no iniciados y la falta de inversión en transmisión eléctrica congelan los rankings.
   - El calentamiento térmico inercial (+0.41 °C/década) deteriora el PUE en provincias del Norte sin que haya nuevas plantas renovables para compensar el consumo auxiliar.

---

## 4. Evolución del Perfil B: Nodos de Inferencia / Edge

En Nodos de Inferencia, la variable rectora es la latencia y la conectividad capilar:

| Jurisdicción | Rank 2026 | Score 2026 | Rank 2036 (Tendencial) | Score 2036 (Tendencial) | $\Delta\text{Score}$ | Motivo de Movimiento |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **CABA** | **1** | 75.16 | **1** | **77.25** | **+2.09** | Líder en talento STEM y cercanía a Las Toninas. |
| **Buenos Aires** | **2** | 63.85 | **2** | **67.45** | **+3.60** | Amarre submarino y expansión logística en AMBA. |
| **Córdoba** | **3** | 61.12 | **3** | **66.88** | **+5.76** | Hub mediterráneo; FTTH saturando al 88%. |
| **Santa Fe** | **4** | 56.09 | **4** | **62.15** | **+6.06** | Polo Rosario/Santa Fe con avance de conectividad. |
| **Mendoza** | **5** | 53.48 | **5** | **58.90** | **+5.42** | Nodo de integración cordillerana hacia Chile. |
| **San Luis** | **6** | 52.80 | **6** | **57.75** | **+4.95** | Histórica inversión en fibra y datacenter provincial. |

---

## 5. Recomendaciones Estratégicas para Inversores y Política Pública

1. **Inversión en Campus de Entrenamiento (Alta Densidad > 50 MW):**
   - **Prioridad Inmediata (2026–2028):** Santa Cruz y Chubut ofrecen la mejor combinación presente y futura de energía eólica masiva y free cooling extremo.
   - **Oportunidad Emergente (2028–2031):** Corrientes surge como el principal hub renovable del Noreste para centros de datos medianos/grandes.
   - **Apuesta de Escala Global (2031–2036):** Si se aprueban regímenes especiales para microrredes off-grid o interconexión austral, Tierra del Fuego representa la mejor localización climática de Sudamérica.
2. **Inversión en Nodos Edge / Inferencia (< 10 MW):**
   - El corredor CABA–Córdoba–Rosario concentra la demanda y retendrá más del 70% de la carga de inferencia nacional hacia 2036.
