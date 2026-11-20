# Diccionario de Datos — Viabilidad IA Data Centers AR

**Versión:** 0.2.0  
**Fecha:** 2026-11-20  
**Tabla objetivo:** `data/03_processed/master_24_jurisdicciones.parquet`  
**Clave primaria:** `jurisdiccion_id` (código INDEC 2 dígitos, string zero-padded)  
**Proyección geográfica:** EPSG:4326 (WGS84)

---

## Convenciones

| Símbolo | Significado |
|---------|------------|
| ↑ | Mayor es mejor (dirección de optimización) |
| ↓ | Menor es mejor (dirección de optimización) |
| 🟢 LISTO | Dato disponible en `jurisdicciones_base.csv` |
| 🟡 PROXY | Valor estimado/indirecto — requiere aprobación explícita antes de usar |
| 🔴 NaN | Sin dato oficial cargado aún — pendiente de ETL en fases posteriores |

Los perfiles de demanda que consumen estas variables están definidos en  
`config/weights_profiles.json` (Perfil A: Campus IA / Perfil B: Nodo Inferencia).

---

## Sección 0 — Ancla Territorial

> Columnas de identidad fija. No participan en el scoring de viabilidad.  
> Fuente: IGN (Instituto Geográfico Nacional) + nomenclador INDEC.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial | Estado |
|---------|------------|--------|-------------|----------------|--------|
| `jurisdiccion_id` | `str` | Código 2 dígitos | — | INDEC — Codificación de Provincias | 🟢 LISTO |
| `jurisdiccion_nombre` | `str` | — | — | INDEC — Nomenclador geográfico | 🟢 LISTO |
| `jurisdiccion_corta` | `str` | ≤ 15 chars | — | Derivado de nombre oficial | 🟢 LISTO |
| `region_argentina` | `str` | Categoría | — | Regionalización macrogeográfica propia (NOA, NEA, Cuyo, Centro, Patagonia, AMBA) | 🟢 LISTO |
| `lat_capital` | `float64` | Grados decimales (WGS84) | — | IGN — Coordenadas de capitales provinciales | 🟢 LISTO |
| `lon_capital` | `float64` | Grados decimales (WGS84) | — | IGN — Coordenadas de capitales provinciales | 🟢 LISTO |

**Notas:**
- `jurisdiccion_id` es la **llave de join obligatoria** en todos los merges del proyecto.
- `region_argentina` = `AMBA` engloba CABA y la provincia de Buenos Aires como región de análisis unificada.

---

## Sección 1 — Energía y Red SADI

> Relevancia principal: **Perfil A (Campus IA)**. Máxima ponderación en `weights_profiles.json`.  
> Fuente objetivo primaria: CAMMESA (informes anuales de demanda y potencia), ENRE, IENOVA.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `sadi_potencia_instalada_mw` | `float64` | MW | ↑ | CAMMESA — Informe Anual de Potencia Instalada por Provincia | 🔴 NaN |
| `sadi_pct_renovable` | `float64` | % (0–100) | ↑ | CAMMESA / MINEM — Mix energético provincial (RenovAR) | 🔴 NaN |
| `sadi_uptime_index` | `float64` | Índice 0–1 | ↑ | ENRE — Interrupciones del Servicio (SAIDI/SAIFI por distribuidora) | 🔴 NaN |
| `sadi_margen_disponible_mw` | `float64` | MW | ↑ | CAMMESA — Margen de reserva operativa por nodo de 500 kV | 🔴 NaN |
| `proyeccion_potencia_2028_mw` | `float64` | MW | ↑ | MINEM — Plan Federal de Transmisión 2028 / Proyectos RenovAR | 🔴 NaN |
| `proyeccion_potencia_2036_mw` | `float64` | MW | ↑ | MINEM — Hoja de Ruta Energética 2030–2036 | 🔴 NaN |
| `potencial_offgrid_score` | `float64` | Índice 0–10 | ↑ | INENCO (solar/eólico) + CONICET (Patagonia) — Recurso renovable off-grid | 🔴 NaN |

**Notas:**
- `sadi_uptime_index` se derivará de SAIDI (System Average Interruption Duration Index): `uptime = 1 - (SAIDI_horas / 8760)`.
- `potencial_offgrid_score` es un índice compuesto (solar + eólico + biomasa). Su fórmula de composición debe aprobarse antes de calcularse (Bloque 3.x).
- Variables de proyección (`2028`, `2036`) alimentarán el módulo Monte Carlo en `src/modeling/`.

---

## Sección 2 — Clima y Agua

> Relevancia principal: **Perfil A** (eficiencia térmica / PUE). Considerado en Perfil B como factor de riesgo.  
> Fuente objetivo primaria: SMN (Servicio Meteorológico Nacional), CONAE, INA.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `temp_media_anual_c` | `float64` | °C | ↓ | SMN — Normales Climatológicas 1991–2020 (por capital provincial) | 🔴 NaN |
| `horas_free_cooling_estimadas` | `float64` | horas/año | ↑ | Derivado de SMN: horas con Tbs < 15°C (umbral estándar data center) | 🟡 PROXY |
| `pue_climatologico_estimado` | `float64` | Adimensional (1.0–2.5) | ↓ | Calculado en `src/gis/`: función de `temp_media_anual_c` y `horas_free_cooling_estimadas` | 🟡 PROXY |
| `indice_estres_hidrico` | `float64` | Índice 0–5 (Aqueduct / WRI) | ↓ | INA / WRI Aqueduct Water Risk Atlas (capa provincial) | 🔴 NaN |

**Notas:**
- `horas_free_cooling_estimadas` y `pue_climatologico_estimado` son **variables derivadas (PROXY)**. Su metodología de cálculo debe documentarse en `docs/metodologia.md` y aprobarse antes de incorporarse al scoring.
- `indice_estres_hidrico` es crítico para data centers con cooling húmedo (torres evaporativas). Escala Aqueduct: 0 = sin estrés, 5 = estrés extremo.

---

## Sección 3 — Conectividad

> Relevancia principal: **Perfil B (Nodo Inferencia/Edge)**. Latencia y redundancia de red.  
> Fuente objetivo primaria: CABASE (IXPs), ENACOM, PeeringDB.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `ixp_cabase_nodos` | `int64` | Cantidad de nodos | ↑ | CABASE — Mapa de IXPs Argentina (cabase.org.ar) | 🔴 NaN |
| `fibra_troncal_cobertura_score` | `float64` | Índice 0–10 | ↑ | ENACOM — Mapa de conectividad (datos.enacom.gob.ar) | 🔴 NaN |
| `distancia_las_toninas_km` | `float64` | km | ↓ | Calculado en `src/gis/`: distancia geodésica desde capital a Las Toninas (38.0°S, 57.4°W) | 🟡 PROXY |

**Notas:**
- Las Toninas (Provincia de Buenos Aires) es el principal punto de aterrizaje de cables submarinos de Argentina (ARBR, AA, GlobeNet, PCCS). Distancia usada como proxy de latencia a conectividad internacional.
- `fibra_troncal_cobertura_score` se construirá en `src/etl/` a partir del dataset ENACOM de localidades con fibra óptica disponible.
- `ixp_cabase_nodos` puede ser 0 para provincias sin nodo IXP propio (ej: gran parte de Patagonia).

---

## Sección 4 — Fiscal y Regulatorio

> Relevancia: **Ambos perfiles**. Factor habilitante / desbloqueador de inversión.  
> Fuente objetivo primaria: Secretaría de Inversiones (RIGI), AFIP/ARCA, legislaturas provinciales.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `rigi_adhesion` | `bool` | Booleano (True/False) | ↑ | Secretaría de Inversiones — Ley 27.742 / adhesiones provinciales | 🔴 NaN |
| `iibb_alicuota_tech_pct` | `float64` | % (0–100) | ↓ | Códigos Fiscales Provinciales — Alícuota IIBB para servicios tecnológicos/comunicaciones | 🔴 NaN |
| `iibb_alicuota_energia_pct` | `float64` | % (0–100) | ↓ | Códigos Fiscales Provinciales — Alícuota IIBB para distribución/venta de energía | 🔴 NaN |
| `indice_promocion_fiscal` | `float64` | Índice 0–10 | ↑ | Compuesto: `rigi_adhesion` + leyes provinciales de promoción IT/parques tecnológicos | 🟡 PROXY |

**Notas:**
- `rigi_adhesion` requiere verificación de actos legislativos provinciales formales, no solo adhesión de intención. Fuente: Boletín Oficial de cada provincia.
- `indice_promocion_fiscal` es un PROXY compuesto. Su fórmula debe aprobarse en Bloque 4.x (Rol: Analista Regulatorio).
- Las alícuotas IIBB cambian frecuentemente. El campo `fecha_corte` en `config/data_sources.yaml` es obligatorio.

---

## Sección 5 — Capital Humano y Riesgo

> Relevancia: **Perfil B** (talento IT para operaciones) y **ambos perfiles** (riesgo físico).  
> Fuente objetivo primaria: INDEC (EPH), INPRES, SMN, IGN.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `densidad_stem_it_score` | `float64` | Índice 0–10 | ↑ | INDEC EPH — Ocupados en rama TIC + matrícula universitaria STEM (SPU) | 🔴 NaN |
| `riesgo_sismico_zona` | `int64` | Zona 0–4 (INPRES-CIRSOC 103) | ↓ | INPRES — Mapa de peligrosidad sísmica de Argentina | 🔴 NaN |
| `riesgo_climatico_score` | `float64` | Índice 0–10 | ↓ | SMN + IGN — Frecuencia de eventos extremos (granizo, inundación, tornado) | 🔴 NaN |
| `riesgo_combinado_score` | `float64` | Índice 0–10 | ↓ | Calculado: combinación ponderada de `riesgo_sismico_zona` + `riesgo_climatico_score` | 🟡 PROXY |

**Notas:**
- `riesgo_sismico_zona`: escala INPRES-CIRSOC 103 — Zona 0 (sin riesgo) a Zona 4 (alto riesgo). Provincias como Mendoza, San Juan y Jujuy tienen zonas 3–4.
- `densidad_stem_it_score` se normalizará a escala 0–10 respecto al máximo provincial observado (CABA o Córdoba).
- `riesgo_combinado_score` es un PROXY. Fórmula pendiente de aprobación (Bloque 5.x).

---

## Variables Futuras (Reservadas — Fase 5)

Estas columnas están reservadas para el módulo `src/finance/` (CAPEX/OPEX/RIGI):

| Columna | Descripción | Fase |
|---------|------------|------|
| `capex_estimado_usd_mw` | CAPEX por MW instalado según perfil | Fase 5 |
| `opex_anual_usd_mw` | OPEX anual por MW | Fase 5 |
| `payback_estimado_años` | Período de recupero de inversión | Fase 5 |
| `van_escenario_base_usd` | VAN en escenario base | Fase 5 |

---

## Registro de Variables NaN y Proxies

| Variable | Motivo NaN/PROXY | Próximo paso | Bloque |
|----------|-----------------|-------------|--------|
| `sadi_potencia_instalada_mw` | Requiere ETL de informes CAMMESA | Scraping/descarga manual PDF | 2.2 |
| `sadi_pct_renovable` | Requiere ETL de informes CAMMESA | Scraping/descarga manual PDF | 2.2 |
| `sadi_uptime_index` | Requiere datos SAIDI/SAIFI por distribuidora | Consulta ENRE | 2.2 |
| `sadi_margen_disponible_mw` | Requiere datos nodales CAMMESA | Consulta CAMMESA | 2.2 |
| `horas_free_cooling_estimadas` | PROXY — fórmula pendiente aprobación | Definir umbral Tbs y procesar SMN | 2.3 |
| `pue_climatologico_estimado` | PROXY — depende de `temp_media_anual_c` | Tras aprobación fórmula | 2.3 |
| `distancia_las_toninas_km` | PROXY — cálculo geodésico pendiente | `src/gis/` con shapely/geopy | 3.1 |
| `indice_promocion_fiscal` | PROXY — fórmula compuesta pendiente | Definir en Bloque 4.x | 4.x |
| `riesgo_combinado_score` | PROXY — ponderación pendiente | Definir en Bloque 5.x | 5.x |

---

*Diccionario mantenido por: Ingeniero de Datos y GIS*  
*Próxima revisión programada: Bloque 2.2 (ingesta de datos CAMMESA/SMN)*
