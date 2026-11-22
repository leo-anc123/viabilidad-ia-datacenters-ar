# Diccionario de Datos — Viabilidad IA Data Centers AR

**Versión:** 0.5.0  
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

## Sección 1 — Energía y Red SADI (v2.1.0)

> Relevancia principal: **Perfil A (Campus IA)**. Máxima ponderación en `weights_profiles.json`.  
> Fuente objetivo primaria: Secretaría de Energía / CAMMESA (Centrales de Generación SADI) + Secretaría de Energía / SESCO Capítulo IV (Gas Natural 2025).

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `sadi_potencia_instalada_mw` | `float64` | MW | ↑ | Sec. Energía / CAMMESA — Centrales de Generación SADI | 🟢 LISTO |
| `sadi_potencia_firme_mw` | `float64` | MW | ↑ | Sec. Energía / CAMMESA — Nuclear + Hidroeléctrica + Ciclo Combinado + Bioenergía | 🟢 LISTO |
| `sadi_mw_renovable` | `float64` | MW | ↑ | Sec. Energía / CAMMESA — Renovables Ley 27.191 | 🟢 LISTO |
| `sadi_pct_renovable` | `float64` | % (0–100) | ↑ | Sec. Energía / CAMMESA — Renovables Ley 27.191 | 🟢 LISTO |
| `sadi_mw_limpia` | `float64` | MW | ↑ | Sec. Energía / CAMMESA — Hidroeléctrica TOTAL + Eólica + Solar + Bioenergía + Nuclear | 🟢 LISTO |
| `sadi_pct_limpia` | `float64` | % (0–100) | ↑ | Sec. Energía / CAMMESA — Matriz Libre de Carbono s/ total provincial | 🟢 LISTO |
| `produccion_gas_operativa_mm3` | `float64` | Mm3/año | ↑ | Sec. Energía de la Nación / SESCO Capítulo IV (Año 2025 completo) | 🟢 LISTO |
| `n_centrales_sadi` | `float64` | Cantidad | ↑ | CAMMESA — Conteo de nodos/centrales de generación | 🟢 LISTO |
| `sadi_diversidad_tech` | `int64` | Cantidad tecnologías | ↑ | CAMMESA — Diversidad tecnológica de generación provincial | 🟢 LISTO |
| `sadi_uptime_index` | `float64` | Índice 0–1 | ↑ | ENRE — SAIDI/SAIFI (solo AMBA; pendiente fuente nacional uniforme) | 🔴 NaN |
| `sadi_margen_disponible_mw` | `float64` | MW | ↑ | CAMMESA — Margen de reserva operativa por nodo de 500 kV | 🔴 NaN |
| `proyeccion_potencia_2028_mw` | `float64` | MW | ↑ | MINEM — Plan Federal de Transmisión 2028 / Proyectos RenovAR | 🔴 NaN |
| `proyeccion_potencia_2036_mw` | `float64` | MW | ↑ | MINEM — Hoja de Ruta Energética 2030–2036 | 🔴 NaN |
| `potencial_offgrid_score` | `float64` | Índice 0–10 | ↑ | INENCO (solar/eólico) + CONICET (Patagonia) — Recurso renovable off-grid | 🔴 NaN |

**Notas:**
- `sadi_potencia_instalada_mw` agrega todas las centrales interconectadas al SADI por provincia. Yacyretá (2.745 MW) se computa en Corrientes y Salto Grande (945 MW) en Entre Ríos. Tierra del Fuego registra 0.0 MW por tratarse de un sistema provincial físicamente aislado.
- `sadi_potencia_firme_mw` aísla la generación de base confiable 24/7 (nuclear, hidroeléctrica, ciclos combinados CCGT y bioenergía), diferenciándola de picos o intermitentes.
- `sadi_pct_limpia` computa la matriz libre de carbono total (sin limitar a mini-hidro) según los compromisos corporativos ESG/RE100 de hyperscalers.
- `produccion_gas_operativa_mm3` computa la extracción real del año 2025 (12 meses) de la Secretaría de Energía, excluyendo offshore federal de Estado Nacional. Tierra del Fuego conserva su puntaje real de gas in-situ (1.351,66 Mm3).

---

## Sección 2 — Clima y Agua

> Relevancia principal: **Perfil A** (eficiencia térmica / PUE). Considerado en Perfil B como factor de riesgo.  
> Fuente objetivo primaria: Open-Meteo Historical API (ERA5 / ECMWF 2000–2023), WRI Aqueduct 4.0.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `temp_media_anual_c` | `float64` | °C | ↓ | Open-Meteo ERA5 / ECMWF (serie diaria 2000–2023) | 🟢 LISTO |
| `temp_max_verano_prom_c` | `float64` | °C | ↓ | Open-Meteo ERA5 / ECMWF (promedio meses DJF 2000–2023) | 🟢 LISTO |
| `horas_free_cooling_estimadas` | `float64` | horas/año | ↑ | Derivado ERA5: promedio anual de horas con Tbs < 15°C (ASHRAE 90.4) | 🟡 PROXY |
| `pue_climatologico_estimado` | `float64` | Adimensional (1.10–1.58) | ↓ | Calculado en `src/gis/`: interpolación lineal PUE mecánico (1.58) a free-cooling (1.10) | 🟡 PROXY |
| `indice_estres_hidrico` | `float64` | Índice 0–5 (Aqueduct / WRI) | ↓ | WRI Aqueduct 4.0 Water Risk Atlas (capa provincial) | 🔴 NaN |

**Notas:**
- `horas_free_cooling_estimadas` y `pue_climatologico_estimado` calculados con fórmulas transparentes aprobadas (Bloque 2.2):
  - Umbral: Tbs < 15.0 °C (ASHRAE 90.4-2019, decisión D1).
  - Factor horario ajuste: 0.70 (concentración de horas frías nocturnas).
  - PUE base mecánico: 1.58 (benchmark LATAM Uptime Institute 2023, decisión D3); PUE mínimo ideal: 1.10.
  - Período climático: 2000–2023 (decisión D4).
- `indice_estres_hidrico` (bws_score WRI Aqueduct 4.0) pendiente de descarga manual de tabla provincial desde portal WRI. Cero datos inventados.

---

## Sección 3 — Conectividad

> Relevancia principal: **Perfil B (Nodo Inferencia/Edge)**. Latencia y redundancia de red.  
> Fuente objetivo primaria: ENACOM, IGN, CABASE (IXPs), PeeringDB.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `distancia_las_toninas_km` | `float64` | km | ↓ | Calculado en `src/gis/`: Haversine WGS84 a Las Toninas (-36.487, -56.696) | 🟢 LISTO |
| `fibra_optica_accesos` | `int64` | Cantidad de accesos | ↑ | ENACOM — Accesos a internet fijo por tecnología | 🟢 LISTO |
| `fibra_optica_pct` | `float64` | % (0–100) | ↑ | Derivado: accesos fibra óptica / total accesos fijos ENACOM | 🟢 LISTO |
| `penetracion_hogares_pct` | `float64` | Accesos / 100 hogares | ↑ | ENACOM — Penetración de internet fijo provincial | 🟢 LISTO |
| `penetracion_habitantes_pct` | `float64` | Accesos / 100 hab. | ↑ | ENACOM — Penetración de internet fijo provincial | 🟢 LISTO |
| `velocidad_media_bajada_mbps` | `float64` | Mbps | ↑ | ENACOM — Velocidad media de descarga provincial | 🟢 LISTO |
| `ixp_cabase_nodos` | `float64` | Cantidad de nodos | ↑ | CABASE — Mapa de IXPs Argentina (cabase.org.ar) | 🔴 NaN |
| `fibra_troncal_cobertura_score` | `float64` | Índice 0–10 | ↑ | ENACOM / ARSAT — Cobertura de fibra troncal (Fase 3) | 🔴 NaN |

**Notas:**
- Las Toninas (Provincia de Buenos Aires, `-36.487, -56.696`) es el principal punto de aterrizaje de cables submarinos de Argentina (ARBR, Tannat, Firmina, Malbec, Atlantis-2, etc.). Distancia usada como proxy de latencia a conectividad internacional mínima.
- `ixp_cabase_nodos`: Mantenido explícitamente en NaN auditable dado que el portal web de CABASE no ofrece descarga estática o API automatizable. Pendiente de carga manual verificada por censo.
- Período de corte ENACOM: 2026-T2 (segundo trimestre de 2026).
- Datos interim consolidados en `data/02_interim/dim_conectividad.csv`.

---

## Sección 4 — Fiscal y Regulatorio

> Relevancia: **Ambos perfiles**. Factor habilitante / desbloqueador de inversión.  
> Fuente objetivo primaria: Secretaría de Inversiones (RIGI), AFIP/ARCA, legislaturas y administraciones tributarias provinciales.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `rigi_adhesion` | `bool` | Booleano (True/False) | ↑ | Secretaría de Inversiones — Ley 27.742 / leyes provinciales de adhesión | 🟢 LISTO |
| `iibb_alicuota_tech_pct` | `float64` | % (0–100) | ↓ | Códigos Fiscales Provinciales — Alícuota IIBB software/IT promovida (LEC/Distritos) o gral | 🟢 LISTO |
| `iibb_alicuota_energia_pct` | `float64` | % (0–100) | ↓ | Cuadros tarifarios provinciales de distribución eléctrica (mantenido en NaN auditable) | 🔴 NaN |
| `indice_promocion_fiscal` | `float64` | Índice 0–10 | ↑ | Compuesto: Score régimen grandes inversiones (RIGI/TDF/RPI) + Score régimen IIBB tech | 🟡 PROXY |

**Notas:**
- `rigi_adhesion` verifica leyes provinciales de adhesión formales sancionadas (18 provincias adheridas, 6 no adheridas). Documentadas exhaustivamente en `docs/supuestos_regulatorios.md`.
- `iibb_alicuota_tech_pct`: consigna 0.0% para jurisdicciones con leyes activas de Economía del Conocimiento o distritos tecnológicos con exención plena para empresas inscriptas; alícuota general de servicios (3.0%–3.5%) para jurisdicciones sin régimen equivalente universal.
- `indice_promocion_fiscal`: suma normalizada de 0 a 10 puntos (hasta 5 pts por gran inversión y hasta 5 pts por régimen IIBB tech). Reconoce el Área Aduanera Especial de Tierra del Fuego (Ley 19.640, 5.0 pts) y el RPI de la Provincia de Buenos Aires (3.5 pts) para evitar penalizaciones distorsivas.
- `iibb_alicuota_energia_pct`: se conserva en `NaN` auditable en las 24 jurisdicciones al depender de esquemas nodales mayoristas (CAMMESA/MATER) y no de alícuotas minoristas planas.

---

## Sección 5 — Capital Humano y Riesgo

> Relevancia: **Perfil B** (talento IT para operaciones) y **ambos perfiles** (riesgo físico).  
> Fuente objetivo primaria: CEP XXI / OEDE, INPRES, SPU, SMN, IGN.

| Columna | Tipo Pandas | Unidad | Optimización | Fuente Oficial Objetivo | Estado |
|---------|------------|--------|-------------|------------------------|--------|
| `puestos_privados_totales` | `int64` | Puestos | ↑ | CEP XXI — Puestos registrados del sector privado (panel mensual) | 🟢 LISTO |
| `puestos_software_clae62` | `int64` | Puestos | ↑ | CEP XXI — CLAE 62: Programación y consultoría informática | 🟢 LISTO |
| `puestos_tic_clae61_63` | `int64` | Puestos | ↑ | CEP XXI — CLAE 61-63: Sector TIC y Servicios de Información | 🟢 LISTO |
| `pct_empleo_tic_privado` | `float64` | % (0–100) | ↑ | Derivado: puestos TIC / puestos privados totales jurisdicción | 🟢 LISTO |
| `densidad_stem_it_score` | `float64` | Índice 0–10 | ↑ | Normalizado relativo al máximo provincial (CABA = 10.0) | 🟢 LISTO |
| `graduados_stem_anual` | `float64` | Personas/año | ↑ | SPU — Anuarios Universitarios (SPU sin desglose provincial en datos abiertos) | 🔴 NaN |
| `riesgo_sismico_zona` | `int64` | Zona 0–4 (INPRES-CIRSOC 103) | ↓ | INPRES — Servicio oficial de zonificación sísmica por coordenadas WGS84 | 🟢 LISTO |
| `riesgo_climatico_score` | `float64` | Índice 0–10 | ↓ | SMN + IGN — Frecuencia de eventos extremos (Fase 3/5) | 🔴 NaN |
| `riesgo_combinado_score` | `float64` | Índice 0–10 | ↓ | Calculado: combinación ponderada de `riesgo_sismico_zona` + `riesgo_climatico_score` | 🟡 PROXY |

**Notas:**
- `riesgo_sismico_zona`: escala reglamentaria INPRES-CIRSOC 103 Parte I — Zona 0 (peligrosidad muy reducida) a Zona 4 (peligrosidad muy elevada). Obtenido mediante consulta al endpoint oficial del INPRES (`zonas_result.php`) con las coordenadas oficiales de las capitales provinciales. San Juan y Mendoza registran Zona 4; Salta, Jujuy y Tierra del Fuego registran Zona 3; provincias pampeanas y mesopotámicas registran Zona 0.
- `puestos_software_clae62`, `puestos_tic_clae61_63` y `pct_empleo_tic_privado`: conservadas explícitamente sin comprimir para habilitar transformaciones logarítmicas o escalados robustos en la Fase 3, mitigando el efecto outlier de CABA.
- `densidad_stem_it_score`: escalado lineal 0–10 tomando el máximo nacional (CABA = 10.0, Córdoba = 4.03, Chaco = 2.59, Santa Fe = 2.54).
- `graduados_stem_anual`: se mantiene en NaN explícito al no contar con desglose oficial a nivel de las 24 jurisdicciones en la base abierta de Araucano-SIPA (agrupada en 5 macrorregiones).
- Datos interim consolidados en `data/02_interim/dim_talento_riesgo.csv`.

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
| `sadi_potencia_instalada_mw` | 🟢 Incorporado | Datos procesados en `dim_energia_sadi.csv` | 2.2 (Listo) |
| `sadi_pct_renovable` | 🟢 Incorporado | Datos procesados en `dim_energia_sadi.csv` | 2.2 (Listo) |
| `temp_media_anual_c` | 🟢 Incorporado | ERA5 diario 2000–2023 en `dim_clima_agua.csv` | 2.2 (Listo) |
| `horas_free_cooling_estimadas` | 🟡 PROXY — Calculado | Tbs < 15°C (ASHRAE 90.4) anualizado | 2.2 (Listo) |
| `pue_climatologico_estimado` | 🟡 PROXY — Calculado | Rango 1.10–1.58 LATAM Uptime en `dim_clima_agua.csv` | 2.2 (Listo) |
| `distancia_las_toninas_km` | 🟢 Incorporado | Haversine WGS84 en `dim_conectividad.csv` | 2.3 (Listo) |
| `fibra_optica_accesos` | 🟢 Incorporado | ENACOM 2026-T2 en `dim_conectividad.csv` | 2.3 (Listo) |
| `velocidad_media_bajada_mbps` | 🟢 Incorporado | ENACOM 2026-T2 en `dim_conectividad.csv` | 2.3 (Listo) |
| `puestos_software_clae62` | 🟢 Incorporado | CEP XXI 2023-11 en `dim_talento_riesgo.csv` | 2.3 (Listo) |
| `puestos_tic_clae61_63` | 🟢 Incorporado | CEP XXI 2023-11 en `dim_talento_riesgo.csv` | 2.3 (Listo) |
| `densidad_stem_it_score` | 🟢 Incorporado | Derivado CEP XXI en `dim_talento_riesgo.csv` | 2.3 (Listo) |
| `riesgo_sismico_zona` | 🟢 Incorporado | INPRES-CIRSOC 103 oficial en `dim_talento_riesgo.csv` | 2.3 (Listo) |
| `rigi_adhesion` | 🟢 Incorporado | 18 adheridas / 6 no adheridas en `dim_fiscal_regulatoria.csv` | 2.4 (Listo) |
| `iibb_alicuota_tech_pct` | 🟢 Incorporado | Leyes LEC y Códigos Fiscales en `dim_fiscal_regulatoria.csv` | 2.4 (Listo) |
| `indice_promocion_fiscal` | 🟡 PROXY — Calculado | Compuesto Inversión + IIBB Tech (0-10) en `dim_fiscal_regulatoria.csv` | 2.4 (Listo) |
| `iibb_alicuota_energia_pct` | 🔴 NaN — Tarifas nodales | Mantener en NaN por complejidad de contratos PPA | 2.4 (Auditable) |
| `ixp_cabase_nodos` | 🔴 NaN — Sin API/CSV abierto | Carga manual verificada por censo CABASE | 2.3 (Manual) |
| `graduados_stem_anual` | 🔴 NaN — Microdatos SPU sin prov. | Pendiente desagregación provincial SPU | 2.3 (Manual) |
| `indice_estres_hidrico` | 🔴 NaN — Formulario web WRI | Descargar manual CSV desde portal Aqueduct | 2.2 (Manual) |
| `sadi_uptime_index` | 🔴 NaN — ENRE solo cubre AMBA | Pendiente fuente nacional uniforme CAMMESA | 2.2 (Manual) |
| `sadi_margen_disponible_mw` | 🔴 NaN — Datos nodales CAMMESA | Descargar informe anual CAMMESA PDF | 2.2 (Manual) |
| `fibra_troncal_cobertura_score` | 🔴 NaN — En construcción | Desarrollar en Bloque 3.x con datos REFEFO/ENACOM | 3.x |
| `riesgo_combinado_score` | 🟡 PROXY — Ponderación | Definir en Bloque 5.x | 5.x |

---

*Diccionario mantenido por: Analista Regulatorio y Negocio / Ingeniero de Datos y GIS*  
*Próxima revisión programada: Fase 3 (Modelado, Clustering y Scoring Multicriterio MCDA)*
