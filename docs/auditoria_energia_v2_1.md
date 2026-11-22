# Auditoría Metodológica del Criterio Energético: Versión v2.1.0 vs v2.0.0
**Proyecto:** Viabilidad de Data Centers y Campus de Inteligencia Artificial en Argentina  
**Fecha de Emisión:** 22 de Noviembre de 2026  
**Autores:** Ingeniero de Datos & Científico de Datos (`AGENTS.md`)  
**Estado:** Validado y Aprobado  

---

## 1. Contexto y Objetivos del Rediseño

La versión previa (`v2.0.0`) calculaba el criterio de energía de las 24 jurisdicciones únicamente mediante dos variables agregadas:
$$\text{subscore\_energia}_{\text{v2.0}} = 0.60 \cdot \text{norm\_potencia\_sadi} + 0.40 \cdot \text{norm\_pct\_renovable}$$

Esta formulación introducía distorsiones estructurales para la toma de decisiones de infraestructura hiper-escalable (Campus de Entrenamiento IA y Nodos Edge):
1. **Falta de Firmeza de Despacho (Baseload):** No distinguía la potencia intermitente (solar fotovoltaica o eólica sin almacenamiento) de la potencia continua 24/7/365 (Nuclear, Hidroeléctrica de embalse, Ciclos Combinados CCGT de alta eficiencia y Bioenergía). Para un Data Center Tier III/IV con SLAs de disponibilidad del 99,98%, la potencia firme es un requisito innegociable.
2. **Omisión de Combustible Primario In-Situ (Vaca Muerta y Cuencas):** No contemplaba la extracción de gas natural en boca de pozo, indispensable para proyectos de autogeneración térmica dedicada, microrredes off-grid y estabilidad de suministro ante picos de demanda estacional.
3. **Subregistro Crítico en Represas Binacionales (Yacyretá):** En el archivo crudo de CAMMESA, la central `YACYRETA` (2.745,0 MW correspondientes a la cuota argentina) figuraba con `provincia = NaN`. El ETL anterior la descartaba por omisión en el cruce de provincias, asignando a Corrientes tan solo 85,6 MW (un subregistro del 97%).

En la versión **v2.1.0**, se rediseñó el pilar energético basándose **exclusivamente en fuentes oficiales operativas actuales** (Secretaría de Energía de la Nación y CAMMESA), con cero datos inventados y cero proyectos proyectados/anunciados.

---

## 2. Definición Metodológica del Subscore de Energía Cuatripartito (v2.1.0)

El nuevo `subscore_energia` se calcula a partir de 4 sub-pilares operativos normalizados en $[0, 100]$:

$$\text{subscore\_energia}_{\text{v2.1}} = 0.35 \cdot S_1 + 0.25 \cdot S_2 + 0.20 \cdot S_3 + 0.20 \cdot S_4$$

$$\sum_{i=1}^4 w_i = 0.35 + 0.25 + 0.20 + 0.20 = 1.000000 \quad (\text{tolerancia } < 10^{-6})$$

### 2.1 Sub-pilar 1: Potencia Firme Despachable ($S_1$, 35%)
- **Métrica:** $\log(1 + \text{MW\_Firme})$, escalado MinMax a $[0, 100]$.
- **Definición Operativa:** Suma de MW instalados y operativos en:
  - **Nuclear (`NUC`):** Embalse (648 MW, Córdoba) y Atucha II (745 MW, Buenos Aires). *Nota de auditoría:* Atucha I (362 MW) no figura en la capa geográfica de 474 puntos provista por la Secretaría de Energía debido a su parada de extensión de vida útil; bajo la regla de no inventar registros, se audita esta ausencia sin alterar el dataset original.
  - **Hidroeléctrica TOTAL (`HI>50`, `HI<50`, `HI`):** Grandes represas (El Chocón, Piedra del Águila, Alicurá, Planicie Banderita, Salto Grande, Yacyretá) y pequeñas hidroeléctricas.
  - **Ciclo Combinado (`CC`, `CC,TG`):** Centrales de ciclo combinado a gas natural y vapor de alta eficiencia (16.340,81 MW a nivel nacional). Se aíslan rigurosamente de turbinas a gas de ciclo abierto (`TG`), turbinas de vapor convencionales (`TV`) y motores diésel (`DI`).
  - **Bioenergía (`BIOM`, `BIOG`):** Centrales térmicas por biomasa y biogás continuo.

### 2.2 Sub-pilar 2: Escala Operativa Total SADI ($S_2$, 25%)
- **Métrica:** $\log(1 + \text{MW\_Total\_SADI})$, escalado MinMax a $[0, 100]$.
- **Definición Operativa:** Capacidad instalada total provincial interconectada a la red nacional. Tierra del Fuego registra estrictamente 0.0 MW por tratarse de un sistema provincial no interconectado.

### 2.3 Sub-pilar 3: Matriz Libre de Carbono ($S_3$, 20%)
- **Métrica:** Porcentaje directo $[0, 100]$.
- **Definición Operativa:** Proporción de generación provincial libre de emisiones directas de GEI según estándares corporativos ESG / RE100 de hyperscalers:
  $$\text{sadi\_pct\_limpia} = \frac{\text{Hidroeléctrica TOTAL} + \text{Eólica} + \text{Solar} + \text{Bioenergía} + \text{Nuclear}}{\text{MW\_Total\_SADI}} \times 100$$
  *(No se limita a renovables Ley 27.191 para no discriminar grandes hidroeléctricas > 50 MW que proveen energía 100% limpia y continua).*

### 2.4 Sub-pilar 4: Seguridad de Combustible Primario ($S_4$, 20%)
- **Métrica:** $\log(1 + \text{Producción\_Gas})$, escalado MinMax a $[0, 100]$.
- **Definición Operativa:** Extracción operativa anual de gas natural en miles de metros cúbicos ($Mm^3$), según la Secretaría de Energía de la Nación (SESCO Capítulo IV), correspondiente al **año 2025 completo** (12 meses continuos).
- **Tratamiento de Filas Extraterritoriales:** El dataset oficial contenía 6.986.207 $Mm^3$ bajo la denominación `"Estado Nacional"`, correspondiente a la plataforma continental offshore federal (Cuenca Austral marina). Dicho volumen fue auditado y **excluido explícitamente de la asignación provincial**, imputándose únicamente la extracción onshore y de jurisdicción provincial.
- **Tratamiento de Tierra del Fuego:** Mantiene $0.0\text{ MW}$ y $0.0\%$ en $S_1, S_2, S_3$, pero recibe su puntaje real en $S_4$ por su producción de $1.351.658\text{ Mm}^3$ (Cuenca Austral), reconociendo su potencial térmico insular sin vulnerar el principio de aislamiento físico del SADI.

---

## 3. Matriz Comparativa Exhaustiva: v2.0 vs v2.1

La siguiente tabla presenta la variación provincia por provincia en el `subscore_energia`, así como su impacto en el Score Compuesto y Ranking del **Perfil A (Campus de Entrenamiento IA)** y **Perfil B (Nodos de Inferencia Edge)**:

| ID | Jurisdicción | Subscore Energía v2.0 | Subscore Energía v2.1 | $\Delta$ Energía | Rank A (v2.0) | Rank A (v2.1) | $\Delta$ Rank A | Rank B (v2.0) | Rank B (v2.1) | $\Delta$ Rank B |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 26 | **Chubut** | 73.08 | **81.95** | +8.88 | #2 | **#1** | **+1** 🟢 | #4 | **#6** | -2 |
| 58 | **Neuquén** | 57.40 | **92.93** | **+35.53** | #8 | **#2** | **+6** 🟢 | #8 | **#4** | **+4** 🟢 |
| 02 | **CABA** | 53.49 | **54.66** | +1.17 | #3 | **#3** | 0 ⚪ | #1 | **#1** | 0 ⚪ |
| 62 | **Río Negro** | 50.56 | **72.95** | **+22.39** | #6 | **#4** | **+2** 🟢 | #6 | **#5** | **+1** 🟢 |
| 14 | **Córdoba** | 55.20 | **64.55** | +9.35 | #5 | **#5** | 0 ⚪ | #3 | **#3** | 0 ⚪ |
| 06 | **Buenos Aires** | 64.68 | **63.80** | -0.88 | #4 | **#6** | -2 🔴 | #2 | **#2** | 0 ⚪ |
| 78 | **Santa Cruz** | 78.00 | **52.92** | -25.08 | #1 | **#7** | -6 🔴 | #9 | **#12** | -3 |
| 50 | **Mendoza** | 49.12 | **74.35** | **+25.23** | #14 | **#8** | **+6** 🟢 | #15 | **#11** | **+4** 🟢 |
| 18 | **Corrientes** | 52.36 | **73.14** | **+20.78** | #15 | **#9** | **+6** 🟢 | #10 | **#8** | **+2** 🟢 |
| 82 | **Santa Fe** | 51.81 | **53.10** | +1.29 | #10 | **#10** | 0 ⚪ | #5 | **#7** | -2 |
| 66 | **Salta** | 55.32 | **67.75** | +12.43 | #12 | **#11** | +1 🟢 | #17 | **#14** | **+3** 🟢 |
| 30 | **Entre Ríos** | 44.67 | **65.68** | **+21.01** | #16 | **#12** | **+4** 🟢 | #11 | **#9** | **+2** 🟢 |
| 38 | **Jujuy** | 70.04 | **55.61** | -14.43 | #9 | **#13** | -4 🔴 | #20 | **#20** | 0 ⚪ |
| 90 | **Tucumán** | 48.79 | **48.11** | -0.68 | #13 | **#14** | -1 🔴 | #12 | **#13** | -1 |
| 70 | **San Juan** | 67.71 | **59.08** | -8.63 | #11 | **#15** | -4 🔴 | #14 | **#16** | -2 |
| 74 | **San Luis** | 67.37 | **38.79** | -28.57 | #7 | **#16** | -9 🔴 | #7 | **#10** | -3 |
| 94 | **Tierra del Fuego**| 0.00 | **16.24** | +16.24 | #19 | **#17** | **+2** 🟢 | #21 | **#21** | 0 ⚪ |
| 22 | **Chaco** | 36.88 | **27.31** | -9.57 | #18 | **#18** | 0 ⚪ | #13 | **#15** | -2 |
| 10 | **Catamarca** | 49.69 | **22.25** | -27.44 | #17 | **#19** | -2 🔴 | #16 | **#19** | -3 |
| 42 | **La Pampa** | 52.64 | **42.35** | -10.30 | #20 | **#20** | 0 ⚪ | #18 | **#17** | +1 🟢 |
| 54 | **Misiones** | 18.01 | **7.51** | -10.51 | #21 | **#21** | 0 ⚪ | #19 | **#18** | +1 🟢 |
| 46 | **La Rioja** | 62.57 | **28.13** | -34.43 | #22 | **#22** | 0 ⚪ | #22 | **#24** | -2 |
| 86 | **Santiago del Estero**| 39.93 | **29.37** | -10.56 | #23 | **#23** | 0 ⚪ | #23 | **#22** | +1 🟢 |
| 34 | **Formosa** | 26.41 | **20.61** | -5.80 | #24 | **#24** | 0 ⚪ | #24 | **#23** | +1 🟢 |

---

## 4. Análisis Diagnóstico de los Movimientos Observados

### 4.1 Ascenso Estratégico de Neuquén (#8 $\rightarrow$ #2 en Perfil A)
Neuquén protagoniza el salto más relevante del ranking, elevando su subscore de energía de 57,40 a **92,93** (+35,53 puntos):
- **Vaca Muerta:** Aporta 35.391,77 $Mm^3$ anuales de gas operativo (74,8% del total nacional continental), lo que le otorga el puntaje máximo en Seguridad de Combustible ($S_4$).
- **Complejo Hidroeléctrico del Comahue:** Concentra 5.902,30 MW de potencia firme de base (El Chocón, Alicurá, Planicie Banderita, Piedra del Águila y Arroyito), proveyendo una matriz 72,09% libre de carbono.
- **Veredicto Técnico:** Neuquén se consolida como el destino más robusto de Argentina para campus de IA de híper-escala que requieran acceso dual a red SADI y autogeneración a boca de pozo.

### 4.2 Liderazgo Consolidado de Chubut (#1 en Perfil A)
Chubut asume el primer puesto del ranking nacional (Score 66,23), superando a Santa Cruz:
- Combina 2.210 MW totales de potencia conectada, 983,9 MW de potencia firme (represa Futaleufú y parques eólicos consolidados con alta factor de capacidad), 2.272 $Mm^3$ de gas operativo en la Cuenca Golfo San Jorge y un PUE climatológico favorable derivado de sus bajas temperaturas estivales.

### 4.3 Revalorización de Centrales Binacionales: Corrientes y Entre Ríos
- **Corrientes (#15 $\rightarrow$ #9 en Perfil A, +6 puestos):** Tras corregir la exclusión histórica de Yacyretá (2.745 MW), Corrientes pasa de registrar 85,6 MW a **2.830,6 MW**, de los cuales 2.796 MW son potencia firme y el 98,78% es libre de carbono.
- **Entre Ríos (#16 $\rightarrow$ #12 en Perfil A, +4 puestos):** La presencia operativa de Salto Grande (945 MW) le asegura 945 MW de potencia firme y un 97,77% de energía limpia.

### 4.4 Ajuste Metodológico de Santa Cruz, San Luis y Catamarca
- **Santa Cruz (#1 $\rightarrow$ #7 en Perfil A, -6 puestos):** En `v2.0`, Santa Cruz lideraba artificialmente debido a su porcentaje renovable del 100% (Ley 27.191) sobre una base pequeña (345 MW eólicos) y su free-cooling extremo. Al penalizar la intermitencia sin potencia de base firme despachable (0.0 MW en ciclos combinados o grandes embalses), se ajusta a un nivel acorde con su infraestructura de red real.
- **San Luis (#7 $\rightarrow$ #16) y Catamarca (#17 $\rightarrow$ #19):** Presentaban altos porcentajes renovables nominales, pero cuentan con escasa potencia firme absoluta (San Luis: 5,3 MW; Catamarca: 0,0 MW). El nuevo pilar de potencia firme sincera su vulnerabilidad técnica.

### 4.5 Resiliencia del Eje Metropolitano (CABA y Buenos Aires)
- **CABA:** Preserva el **#1 indiscutido en Nodos Edge** (Score 75,34) y el #3 en Campus IA (Score 63,65). Dispone de 3.170 MW firmes (ciclos combinados de Central Puerto y Costanera), máxima conectividad y talento IT.
- **Buenos Aires:** Mantiene el **#2 en Nodos Edge** (Score 64,69) y el #6 en Campus IA (Score 58,73), sustentada por 6.101 MW firmes (Atucha II y grandes ciclos combinados de Campana, Ensenada y Bahía Blanca).

---

## 5. Trazabilidad de Integridad del Repositorio
- **Fuentes oficiales registradas:** `config/data_sources.yaml` y `data/04_outputs/data_freshness.json` (v2.1.0).
- **Consistencia referencial:** 474 centrales SADI verificadas en `geo_centrales_sadi.csv` e `ivid_payload.json`.
- **Filtros web actualizados:** 6 categorías operativas en mapa interactivo: *Hidroeléctrica* (62), *Térmica* (205), *Solar* (84), *Eólica* (71), *Bioenergía* (50) y *Nuclear* (2).
- **Módulos intactos:** `src/finance/` y `app/main.py` permanecen 100% inalterados.
- **Validación automatizada:** 4/4 suites de pruebas ejecutadas con estado `PASS` (`validate_master`, `validate_mcda`, `validate_fase3`, `validate_forecasting`).
