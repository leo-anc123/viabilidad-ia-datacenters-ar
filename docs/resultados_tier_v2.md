# Auditoría Comparativa de Resultados: Modelo v1.0.0 vs. v2.0.0-alpha.1
## Incorporación de la 6.ª Dimensión: Aptitud Territorial Tier (Tier-Readiness)

**Fecha:** 2026-11-21  
**Autor:** Científico de Datos — Proyecto Viabilidad Data Centers e IA en Argentina  
**Datasets comparados:**  
- Base v1.0.0 (5 dimensiones): `data/04_outputs/scores_mcda_perfiles.parquet` (histórico)
- Modelo v2.0.0-alpha.1 (6 dimensiones): `data/04_outputs/scores_mcda_perfiles.parquet` (actualizado)

---

## 1. Resumen Ejecutivo de la Evolución Metodológica

La transición de la versión `v1.0.0` (Fase 4 MVP) a `v2.0.0-alpha.1` (Iteración 2 — Bloque 2A) introduce por primera vez en el modelo una evaluación cuantitativa y explícita de **misión crítica**: la **Aptitud Territorial Tier (Tier-Readiness)**.

Mientras el modelo `v1.0.0` medía dotación bruta de recursos (volumen total de MW, frío promedio anual y conectividad a Las Toninas), el nuevo modelo `v2.0.0-alpha.1` evalúa la resiliencia física, operativa y estructural del territorio frente a estándares de disponibilidad Tier III y Tier IV de Uptime Institute:
1. **Redundancia y diversidad eléctrica:** Presencia de múltiples centrales y diversas tecnologías en la provincia para evitar colapsos monofuente (CAMMESA).
2. **Estabilidad sísmica de sitio:** Zonificación INPRES-CIRSOC 103 (protección de racks, generadores y chillers).
3. **Resiliencia térmica operativa:** Temperatura máxima estival promedio (resistencia a estrés térmico y enfriamiento continuo).
4. **Madurez de red:** Disponibilidad de fibra óptica y ancho de banda para acometidas subterráneas disjuntas (ENACOM).

---

## 2. Comparativa Top 10 — Perfil A: Campus de Entrenamiento IA (Alta Densidad)

Ponderación v1.0.0: Energía 35%, Clima 25%, Fiscal 20%, Conectividad 10%, Talento/Riesgo 10%.  
Ponderación v2.0.0-alpha.1: Energía 30%, Clima 20%, **Tier-Readiness 15%**, Fiscal 15%, Conectividad 10%, Talento/Riesgo 10%.

| Jurisdicción | Rank v1.0.0 | Score v1.0.0 | Rank v2.0.0 | Score v2.0.0 | Variación Rank | Tier-Readiness (0–100) | Diagnóstico Técnico de Movimiento |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Santa Cruz** | #1 | 67.00 | **#1** | **64.09** | ➡️ 0 | 55.12 | Retiene el liderazgo absoluto por su clima frío extremo (PUE 1.25) y gran potencia eólica. |
| **Chubut** | #2 | 64.87 | **#2** | **63.57** | ➡️ 0 | 63.26 | Fuerte resiliencia: alta potencia renovable SADI, baja sismicidad y adhesión plena al RIGI. |
| **CABA** | #3 | 64.36 | **#3** | **63.30** | ➡️ 0 | 53.21 | Estabilidad sólida impulsada por su marco fiscal (Distrito Tech) y masiva infraestructura de red. |
| **Buenos Aires** | #9 | 55.92 | **#4** | **58.99** | ⬆️ **+5** | **72.35** | **Gran ganadora:** 82 centrales SADI, 9 tecnologías, sismicidad cero (Zona 0) y alta velocidad de red. |
| **Córdoba** | #7 | 56.47 | **#5** | **56.53** | ⬆️ **+2** | **59.98** | Escala por su matriz hidro/térmica diversificada (42 centrales, 11 tecnologías) y RIGI. |
| **Río Negro** | #8 | 56.45 | **#6** | **55.68** | ⬆️ **+2** | 57.27 | Balance favorable entre free-cooling patagónico y moderada sismicidad. |
| **San Luis** | #4 | 58.50 | **#7** | **55.09** | ⬇️ **-3** | 40.73 | Cae 3 puestos: menor diversidad de generación local (3 tecnologías) y verano caluroso. |
| **Neuquén** | #6 | 56.59 | **#8** | **54.78** | ⬇️ **-2** | 50.33 | Penalizada moderadamente por temperatura estival y menor redundancia de fibra vs. PBA/CBA. |
| **Jujuy** | #5 | 58.43 | **#9** | **53.45** | ⬇️ **-4** | 36.05 | Cae 4 puestos: elevada sismicidad (Zona 3 CIRSOC 103) y concentración monofuente solar. |
| **Santa Fe** | #12 | 52.88 | **#10** | **53.31** | ⬆️ **+2** | **56.04** | Ingresa al Top 10 desbancando a San Juan gracias a su sismicidad nula (Zona 0) y red SADI. |

*Nota sobre San Juan:* Cae del puesto #10 (v1.0.0: 54.90) al puesto #11 (v2.0.0: 50.41) debido a que su puntaje de Tier-Readiness es de solo **32.18 pts** (Peligrosidad sísmica extrema: Zona 4 CIRSOC 103 y temperatura estival DJF elevada).

---

## 3. Comparativa Top 10 — Perfil B: Nodos de Inferencia / Edge

Ponderación v1.0.0: Conectividad 35%, Talento/Riesgo 25%, Fiscal 15%, Energía 15%, Clima 10%.  
Ponderación v2.0.0-alpha.1: Conectividad 30%, Talento/Riesgo 20%, **Tier-Readiness 15%**, Energía 15%, Fiscal 10%, Clima 10%.

| Jurisdicción | Rank v1.0.0 | Score v1.0.0 | Rank v2.0.0 | Score v2.0.0 | Variación Rank | Tier-Readiness (0–100) | Diagnóstico Técnico de Movimiento |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **CABA** | #1 | 81.58 | **#1** | **75.16** | ➡️ 0 | 53.21 | Líder indiscutido en ultra-baja latencia, ecosistema de IXPs CABASE y talento STEM. |
| **Buenos Aires** | #2 | 63.89 | **#2** | **64.83** | ➡️ 0 | **72.35** | Se consolida como escolta inmediata y acorta brecha gracias a su máximo Tier-Readiness nacional. |
| **Córdoba** | #3 | 59.17 | **#3** | **57.53** | ➡️ 0 | 59.98 | Mantiene el podio: segundo polo tecnológico del país y alta capilaridad de telecomunicaciones. |
| **Chubut** | #6 | 56.35 | **#4** | **56.54** | ⬆️ **+2** | 63.26 | Sube al 4.° puesto: alta estabilidad sísmica, clima favorable y buena conectividad costera. |
| **Santa Fe** | #4 | 57.99 | **#5** | **55.76** | ⬇️ -1 | 56.04 | Mantiene posición de élite en el Corredor Central (Rosario/Santa Fe). |
| **Río Negro** | #7 | 55.72 | **#6** | **54.53** | ⬆️ **+1** | 57.27 | Posición competitiva gracias a INVAP/Bariloche y bajo riesgo telco. |
| **San Luis** | #5 | 56.56 | **#7** | **53.09** | ⬇️ -2 | 40.73 | Cede posiciones ante provincias con mayor robustez de acometida y diversidad SADI. |
| **Neuquén** | #8 | 54.82 | **#8** | **52.83** | ➡️ 0 | 50.33 | Polo regional patagónico estable en octavo lugar. |
| **Santa Cruz** | #11 | 49.80 | **#9** | **50.67** | ⬆️ **+2** | 55.12 | Ingresa al Top 10 desbancando a Entre Ríos por su alta resiliencia térmica y eólica. |
| **Corrientes** | #10 | 50.27 | **#10** | **47.77** | ➡️ 0 | 46.71 | Mantiene presencia en Top 10 por Yacyretá y sismicidad Zona 0. |

---

## 4. Hallazgos Analíticos y Conclusiones de Negocio

1. **Corrección del Sesgo de Recursos Crudos:**  
   En `v1.0.0`, una provincia podía calificar en el Top 5 simplemente por tener un recurso sobresaliente (ej. radiación solar extrema en Jujuy o beneficios fiscales en San Luis). `v2.0.0-alpha.1` penaliza la vulnerabilidad estructural: un centro de datos no puede operar con tolerancia a fallas si está en una zona de alta actividad sísmica (Zona 3 o 4) o si depende de un único tipo de generación eléctrica.
2. **El "Salto Metropolitano" de Buenos Aires:**  
   Buenos Aires es la jurisdicción más beneficiada por la dimensión Tier-Readiness (+5 puestos en Campus IA, subiendo al #4). Esto refleja una realidad ineludible de la infraestructura de misión crítica: la Provincia de Buenos Aires concentra 82 centrales generadoras interconectadas, 9 tecnologías disjuntas, riesgo sísmico nulo y la mayor capilaridad de fibra del país.
3. **El Escudo Patagónico:**  
   Tanto Santa Cruz (#1) como Chubut (#2) prueban ser robustas frente a la introducción de criterios Tier. Su combinación de PUE climatológico récord (< 1.25), baja sismicidad y enorme penetración de energía eólica las mantiene como los destinos preferenciales de Latinoamérica para Campus de Entrenamiento de Inteligencia Artificial.
4. **Desacople de Sistemas Aislados:**  
   Tierra del Fuego (sistema insular no interconectado) queda debidamente delimitada: su PUE climatológico es excepcional (1.245), pero su Tier-Readiness (31.51) advierte a los inversores que cualquier proyecto allí requerirá microredes dedicadas off-grid completas, ya que no puede apoyarse en redundancia de red mayorista SADI.
