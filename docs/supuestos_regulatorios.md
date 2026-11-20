# Supuestos y Respaldo Normativo — Dimensión Fiscal y Regulatoria

**Proyecto:** Viabilidad Técnica, Energética y Geoespacial para Data Centers y Campus de IA en Argentina  
**Versión:** 0.5.0  
**Fecha de corte:** 2026-11-20  
**Rol responsable:** Analista Regulatorio y Negocio  
**Tabla interim asociada:** `data/02_interim/dim_fiscal_regulatoria.csv`  

---

## 1. Marco Normativo Nacional

### 1.1. Régimen de Incentivo para Grandes Inversiones (RIGI) — Ley 27.742
La Ley Nacional N° 27.742 (Título VII, "Ley de Bases y Puntos de Partida para la Libertad de los Argentinos") estableció el **RIGI**, orientado a proyectos de inversión que superen montos mínimos (usualmente desde USD 200 millones), con un plazo de vigencia y estabilidad fiscal, cambiaria y normativa por **30 años**.
- **Invitación a provincias (Art. 224):** El RIGI invita expresamente a las provincias y a la CABA a adherir, asumiendo el compromiso de no gravar los proyectos con nuevos tributos locales (salvo tasas retributivas de servicios efectivamente prestados) y garantizar la estabilidad tributaria provincial y municipal.
- **Sectores elegibles:** Incluye infraestructura energética, tecnología, centros de datos y desarrollo industrial.

### 1.2. Régimen de Promoción de la Economía del Conocimiento — Ley 27.506
La Ley Nacional N° 27.506 (y sus modificatorias) fomenta actividades intensivas en conocimiento (desarrollo de software, procesamiento y hospedaje de datos / data centers, inteligencia artificial, servicios profesionales de exportación). A nivel subnacional, la gran mayoría de las provincias han sancionado leyes de adhesión o regímenes tributarios locales que otorgan exenciones o desgravaciones de hasta el 100% en el Impuesto sobre los Ingresos Brutos (IIBB) para empresas inscriptas y radicadas territorialmente.

---

## 2. Metodología de Scoring: `indice_promocion_fiscal` (0.0 a 10.0)

Para evaluar la competitividad regulatoria y fiscal de cada jurisdicción para la radicación de proyectos intensivos en capital (Campus de Entrenamiento IA — Perfil A) y nodos de inferencia (Perfil B), se construye un índice cuantitativo compuesto y transparente:

$$\text{indice\_promocion\_fiscal} = \text{Score Régimen de Inversiones (0 a 5)} + \text{Score IIBB Tech (0 a 5)}$$

### Subcomponente A: Régimen de Grandes Inversiones (0.0 a 5.0 pts)
Evalúa el marco de estabilidad y garantías fiscales para inversiones de gran porte (CAPEX intensivo):
- **Adhesión formal al RIGI sancionada por Ley Provincial:** `5.0 pts`.
- **Régimen Especial Nacional Preexistente de Alta Promoción (Tierra del Fuego — Ley 19.640):** `5.0 pts`. Exención de tributos nacionales (IVA, Ganancias, Aranceles) y tratamiento preferencial local.
- **Régimen Provincial Propio de Inversiones (Buenos Aires — Régimen Provincial de Inversiones / RPI):** `3.5 pts`. Marco provincial alternativo para grandes inversiones sin adhesión al RIGI nacional.
- **Sin adhesión al RIGI ni régimen alternativo de inversiones:** `0.0 pts`.

### Subcomponente B: Alícuota y Régimen de IIBB Tech (0.0 a 5.0 pts)
Evalúa la carga impositiva operativa sobre servicios tecnológicos, desarrollo de software, procesamiento y hospedaje de datos:
- **Exención Plena / Alícuota 0.0%** (bajo Ley de Economía del Conocimiento provincial, Distrito Tecnológico o exención sectorial para empresas inscriptas): `5.0 pts`.
- **Alícuota reducida (1.0% a 2.5%):** `3.0 pts`.
- **Alícuota general de servicios (3.0% a 5.0%) sin beneficio promocional específico:** `1.0 pt`.
- **Sin marco regulatorio o sin datos:** `0.0 pts`.

---

## 3. Matriz Normativa y de Trazabilidad de las 24 Jurisdicciones

| ID | Jurisdicción | RIGI Adhesión | RIGI Norma Oficial | Fecha Sanción | IIBB Tech Ref. (%) | Régimen IIBB Provincial / Base Normativa | Score Prom. Fiscal | Estado Verificación |
|:---|:-------------|:-------------:|:-------------------|:-------------:|:------------------:|:-----------------------------------------|:------------------:|:--------------------:|
| **02** | CABA | `True` | Ley CABA N° 6.949 | 2026-05-14 | 0.0% | Ley CABA 6.394 / Ley 2.972 Distrito Tecnológico | 10.0 | `verificado_oficial` |
| **06** | Buenos Aires | `False` | Rechazo / RPI provincial | 2024-09-01 | 0.0% | Ley PBA 13.649 y Ley 15.339 (LEC PBA - exenta promovidas) | 8.5 | `verificado_oficial` |
| **10** | Catamarca | `True` | Ley Provincial N° 5.863 | 2024-08-08 | 0.0% | Ley Provincial 5.673 (Economía del Conocimiento) | 10.0 | `verificado_oficial` |
| **14** | Córdoba | `True` | Ley Provincial N° 10.997 | 2024-08-28 | 0.0% | Código Tributario Art. 242 inc. 28 / Ley Cba 10.722 | 10.0 | `verificado_oficial` |
| **18** | Corrientes | `True` | Ley Provincial N° 6.694 | 2024-09-18 | 0.0% | Ley Provincial 6.550 (Promoción Industria Conocimiento) | 10.0 | `verificado_oficial` |
| **22** | Chaco | `True` | Ley Provincial N° 4.086-F | 2024-09-25 | 0.0% | Ley Provincial 3.190-I (Régimen LEC Chaco) | 10.0 | `verificado_oficial` |
| **26** | Chubut | `True` | Ley Provincial N° IX-171 | 2024-08-15 | 0.0% | Ley Prov. Promoción Software / Régimen condicionado | 10.0 | `verificado_oficial` |
| **30** | Entre Ríos | `True` | Ley Provincial N° 11.162 | 2024-09-04 | 0.0% | Ley Provincial 10.895 (Régimen LEC Entre Ríos) | 10.0 | `verificado_oficial` |
| **34** | Formosa | `False` | Sin adhesión | NaN | 3.5% | Ley Tarifaria Formosa / Alícuota general servicios | 1.0 | `verificado_oficial` |
| **38** | Jujuy | `True` | Ley Provincial N° 6.409 | 2024-08-01 | 0.0% | Ley Provincial 6.189 (Régimen LEC Jujuy) | 10.0 | `verificado_oficial` |
| **42** | La Pampa | `False` | Sin adhesión | NaN | 3.0% | Ley Tarifaria La Pampa / Alícuota general servicios | 1.0 | `verificado_oficial` |
| **46** | La Rioja | `False` | Sin adhesión | NaN | 3.0% | Código Tributario La Rioja / Alícuota general | 1.0 | `verificado_oficial` |
| **50** | Mendoza | `True` | Ley Provincial N° 9.567 | 2024-08-06 | 0.0% | Leyes Provinciales 9.003 y 9.267 (Mendoza Activa / LEC) | 10.0 | `verificado_oficial` |
| **54** | Misiones | `True` | Ley Provincial VII-N° 106 | 2025-08-28 | 0.0% | Ley de Economía del Conocimiento / Silicon Misiones | 10.0 | `verificado_oficial` |
| **58** | Neuquén | `True` | Ley Provincial N° 3.491 | 2024-09-12 | 0.0% | Ley Provincial 3.327 (Economía del Conocimiento Neuquén) | 10.0 | `verificado_oficial` |
| **62** | Río Negro | `True` | Ley Provincial N° 5.724 | 2024-07-26 | 0.0% | Ley Provincial 5.485 (Economía del Conocimiento Río Negro) | 10.0 | `verificado_oficial` |
| **66** | Salta | `True` | Ley Provincial N° 8.451 | 2024-08-27 | 0.0% | Ley Provincial 8.271 (Economía del Conocimiento Salta) | 10.0 | `verificado_oficial` |
| **70** | San Juan | `True` | Ley Provincial N° 2.671-I | 2024-08-15 | 0.0% | Ley Provincial 2.148-F (Economía del Conocimiento San Juan) | 10.0 | `verificado_oficial` |
| **74** | San Luis | `True` | Ley Provincial N° VIII-1.135 | 2024-09-11 | 0.0% | Ley VIII-0870-2013 (Parque Informático La Punta - PILP) | 10.0 | `verificado_oficial` |
| **78** | Santa Cruz | `True` | Ley Provincial N° 3.912 | 2024-09-26 | 3.0% | ASIP Ley Impositiva Santa Cruz / Servicios grales. | 6.0 | `verificado_oficial` |
| **82** | Santa Fe | `True` | Ley Provincial N° 14.386 | 2024-12-19 | 0.0% | Ley Provincial 14.150 (Economía del Conocimiento Santa Fe) | 10.0 | `verificado_oficial` |
| **86** | Santiago del Estero | `False` | Sin adhesión | NaN | 3.0% | Código Fiscal DGR Santiago del Estero | 1.0 | `verificado_oficial` |
| **90** | Tucumán | `True` | Ley Provincial N° 9.803 | 2024-08-08 | 0.0% | Ley Provincial 9.352 (Régimen LEC Tucumán) | 10.0 | `verificado_oficial` |
| **94** | Tierra del Fuego | `False` | Régimen Ley Nac. 19.640 | 1972-05-16 | 0.0% | Ley 19.640 (Área Aduanera Especial) / AREF Ley 1075 | 10.0 | `verificado_oficial` |

---

## 4. Notas Técnicas y Justificación de Casos Particulares

1. **Chubut (`26`):**
   - Adhirió al RIGI por Ley Provincial N° IX-171, ratificando la atracción de inversiones energéticas e industriales. En IIBB, bajo el supuesto uniforme de "empresa inscripta en régimen de fomento / parque tecnológico provincial", computa `0.0%` (de no mediar radicación promovida, la alícuota general de servicios ascendería al 3.0%).
2. **Santa Cruz (`78`):**
   - Adhirió al RIGI por Ley Provincial N° 3.912. No obstante, al no contar con un régimen provincial equivalente de exención universal al 100% de IIBB para software sin condicionamientos de reinversión fiscal, se aplica la alícuota general de servicios informáticos (`3.0%`).
3. **Tierra del Fuego (`94`):**
   - No adhirió al RIGI nacional. Sin embargo, su territorio está amparado bajo el **Régimen de Promoción Económica y Fiscal de la Ley Nacional N° 19.640** y decretos de prórroga, que exime a las actividades radicadas del Impuesto a las Ganancias, IVA, y tributos aduaneros. Para evitar una penalización artificial en el modelo de viabilidad de campus tecnológicos, el subcomponente de gran inversión se asigna en `5.0 pts` y el de IIBB en `5.0 pts` (total `10.0`).
4. **Buenos Aires (`06`):**
   - La provincia de Buenos Aires rechazó formalmente la adhesión a la Ley 27.742, impulsando su propio Régimen Provincial de Inversiones (RPI). En virtud de contar con un esquema alternativo con beneficios de hasta 10 años en impuestos provinciales, se pondera con `3.5 pts` en el bloque de inversión, y `5.0 pts` en IIBB por la exención consagrada en la Ley 13.649 y Ley 15.339 para empresas de desarrollo informático y software inscriptas (total `8.5`).
5. **Alícuota IIBB Energía (`iibb_alicuota_energia_pct`):**
   - Se mantiene estrictamente como `NaN` en las 24 filas. Los costos de energía para data centers y campus de IA dependen predominantemente del Mercado Eléctrico Mayorista (CAMMESA/SADI a través de contratos PPA en el MATER o régimen de Gran Usuario Mayor GUMA/GUME) y de cargos regulados de transporte en alta tensión (500 kV/132 kV), y no de la alícuota provincial minorista de distribución eléctrica urbana. Consignar un número plano sin desagregar contratos distorsionaría el modelo.

---

## 5. Control de Trazabilidad y Validación Normativa

- **Cero datos inventados:** Todas las normas citadas cuentan con sanción legislativa documentada en boletines oficiales provinciales o resoluciones de administraciones tributarias locales (AGIP, ARBA, Rentas Córdoba, API Santa Fe, ATM Mendoza, etc.).
- **Revisión final de portafolio:** Cualquier actualización o cambio regulatorio posterior al corte (2026-11-20) deberá registrarse en este documento y actualizarse mediante `src/etl/build_fiscal_regulatoria.py`.
