# Reporte de Control de Calidad y Cobertura — Fase 2 (v0.5.0)

**Fecha de generación:** 2026-11-21 10:36:37  
**Tabla auditada:** `data/03_processed/master_24_jurisdicciones.parquet`  
**Registros territoriales:** 24 jurisdicciones (23 provincias + CABA) — 100% match ancla INDEC.  

---

## 1. Resumen Ejecutivo de Cobertura

- **Total de columnas unificadas:** 63
- **Columnas 100% completas (0% nulos):** 49 (77.8%)
- **Columnas con nulos parciales justificados:** 1 (1.6%)
- **Columnas 100% NaN documentadas para Fase 3/4/5:** 13 (20.6%)

---

## 2. Cobertura por Dimensión Analítica

| Dimensión | Columnas Totales | 100% Completas | Parciales | 100% NaN | Estado de Viabilidad |
|:---|:---:|:---:|:---:|:---:|:---|
| Sección 0 — Ancla Territorial | 6 | 6 | 0 | 0 | 🟢 Operativa |
| Sección 1 — Energía y Red SADI | 11 | 6 | 0 | 5 | 🟡 Operativa c/ pendientes |
| Sección 2 — Clima y Agua | 13 | 11 | 0 | 2 | 🟡 Operativa c/ pendientes |
| Sección 3 — Conectividad | 10 | 8 | 0 | 2 | 🟡 Operativa c/ pendientes |
| Sección 4 — Fiscal y Regulatorio | 10 | 8 | 1 | 1 | 🟡 Operativa c/ pendientes |
| Sección 5 — Capital Humano y Riesgo | 13 | 10 | 0 | 3 | 🟡 Operativa c/ pendientes |

---

## 3. Matriz Exhaustiva de Columnas y Tratamiento para Fase 3

| Sección | Columna | No-Nulos | Nulos | % Nulos | Estado | Tratamiento / Decisión Fase 3 |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| Ancla Territorial | `jurisdiccion_id` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Ancla Territorial | `jurisdiccion_nombre` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Ancla Territorial | `jurisdiccion_corta` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Ancla Territorial | `region_argentina` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Ancla Territorial | `lat_capital` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Ancla Territorial | `lon_capital` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `sadi_potencia_instalada_mw` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `sadi_pct_renovable` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `sadi_uptime_index` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Energía y Red SADI | `sadi_margen_disponible_mw` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Energía y Red SADI | `proyeccion_potencia_2028_mw` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Energía y Red SADI | `proyeccion_potencia_2036_mw` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Energía y Red SADI | `potencial_offgrid_score` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Energía y Red SADI | `n_centrales_sadi` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `sadi_diversidad_tech` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `fuente_energia` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Energía y Red SADI | `fecha_corte_energia` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `temp_media_anual_c` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `temp_max_verano_prom_c` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `horas_free_cooling_estimadas` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `pue_climatologico_estimado` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `indice_estres_hidrico` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Clima y Agua | `n_dias_datos` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `fuente_clima` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `fuente_hidrica` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Clima y Agua | `periodo_referencia` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `umbral_free_cooling_c` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `pue_base_mecanico` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `pue_min_free_cooling` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Clima y Agua | `factor_horario_ajuste` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `distancia_las_toninas_km` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `fibra_optica_accesos` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `fibra_optica_pct` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `penetracion_hogares_pct` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `penetracion_habitantes_pct` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `velocidad_media_bajada_mbps` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `ixp_cabase_nodos` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Conectividad | `fibra_troncal_cobertura_score` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Conectividad | `fuente_conectividad` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Conectividad | `fecha_corte_conectividad` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `rigi_adhesion` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `rigi_normativa` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `rigi_fecha_sancion` | 20 | 4 | 16.7% | 🟡 Parcial | Valor nulo con significado de negocio (ej. sin fecha por no adhesión). |
| Fiscal y Regulatorio | `iibb_alicuota_tech_pct` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `iibb_regimen_promocion` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `iibb_alicuota_energia_pct` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Fiscal y Regulatorio | `indice_promocion_fiscal` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `estado_verificacion_normativa` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `fuente_fiscal` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Fiscal y Regulatorio | `fecha_corte_fiscal` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `puestos_privados_totales` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `puestos_software_clae62` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `puestos_tic_clae61_63` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `pct_empleo_tic_privado` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `densidad_stem_it_score` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `graduados_stem_anual` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Capital Humano y Riesgo | `riesgo_sismico_zona` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `riesgo_climatico_score` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Capital Humano y Riesgo | `riesgo_combinado_score` | 0 | 24 | 100.0% | 🔴 100% NaN | Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3. |
| Capital Humano y Riesgo | `fuente_talento` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `fecha_corte_talento` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `fuente_riesgo_sismico` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |
| Capital Humano y Riesgo | `fecha_corte_riesgo_sismico` | 24 | 0 | 0.0% | 🟢 Completo | Ingresa directamente al modelo multicriterio (MCDA) / clustering. |

---

## 4. Conclusión de Calidad

1. **Integridad Territorial:** 24/24 jurisdicciones oficiales argentinas presentes y validadas contra el ancla INDEC.
2. **Cero Datos Inventados:** No se aplicó ninguna imputación sintética en crudos ni en interim. Todas las variables NaN cuentan con justificación metodológica en `docs/data_dictionary.md`.
3. **Compatibilidad:** La exportación Parquet preserva tipos precisos para Scikit-learn en Fase 3; el CSV espejo permite inspección en Excel y visualización en Power BI.
