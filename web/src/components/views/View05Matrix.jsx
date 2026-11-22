import React, { useState, useMemo } from 'react';
import { useAppData } from '../../context/DataContext';
import { Search, RotateCcw, ArrowUpDown, ShieldCheck, Sparkles } from 'lucide-react';

const DIMENSION_COLS = [
  { id: 'subscore_energia', label: 'Energía', short: 'Energía' },
  { id: 'subscore_clima', label: 'Clima', short: 'Clima' },
  { id: 'subscore_conectividad', label: 'Conectividad', short: 'Conect.' },
  { id: 'subscore_fiscal', label: 'Fiscal / RIGI', short: 'Fiscal' },
  { id: 'subscore_talento_riesgo', label: 'Talento / Riesgo', short: 'Talento' },
  { id: 'subscore_tier_readiness', label: 'Tier-Readiness', short: 'Tier' },
];

function getHeatmapClass(val) {
  if (val >= 80) {
    return 'bg-[#132B24] text-[#34D399] border border-[#1A5336]';
  }
  if (val >= 60) {
    return 'bg-[#132338] text-[#38BDF8] border border-[#1D4063]';
  }
  return 'bg-[#33171D] text-[#F87171] border border-[#5E1E26]';
}

export default function View05Matrix() {
  const { data, activePerfil, changePerfil, setSelectedProvinceId } = useAppData();

  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('score_desc'); // 'score_desc', 'score_asc', 'nombre_asc', 'prob_top3', o dimensionId

  if (!data) return null;

  const { jurisdicciones } = data;

  const resetFilters = () => {
    setSearchTerm('');
    setSortBy('score_desc');
  };

  // Construir filas aplanadas con scores del perfil activo
  const tableRows = useMemo(() => {
    return jurisdicciones.map((j) => {
      const pData = j.scores_perfiles?.[activePerfil] || {};
      return {
        id: j.id,
        nombre: j.nombre,
        corta: j.corta || j.nombre,
        region: j.region,
        score: pData.score_base || 0,
        rank: pData.rank_base || 99,
        probTop3: pData.prob_top3_pct || 0,
        cluster: j.cluster?.nombre || 'General',
        subscores: j.subscores || {},
      };
    });
  }, [jurisdicciones, activePerfil]);

  // Filtrado y Ordenamiento
  const filteredAndSortedRows = useMemo(() => {
    let result = tableRows.filter((r) => {
      const q = searchTerm.toLowerCase().trim();
      if (!q) return true;
      return (
        r.nombre.toLowerCase().includes(q) ||
        r.corta.toLowerCase().includes(q) ||
        r.region.toLowerCase().includes(q) ||
        r.cluster.toLowerCase().includes(q)
      );
    });

    result.sort((a, b) => {
      if (sortBy === 'score_desc') return b.score - a.score;
      if (sortBy === 'score_asc') return a.score - b.score;
      if (sortBy === 'nombre_asc') return a.nombre.localeCompare(b.nombre);
      if (sortBy === 'prob_top3') return b.probTop3 - a.probTop3;
      if (sortBy.startsWith('dim_')) {
        const dimId = sortBy.replace('dim_', '');
        return (b.subscores[dimId] || 0) - (a.subscores[dimId] || 0);
      }
      return 0;
    });

    return result;
  }, [tableRows, searchTerm, sortBy]);

  const perfilesTabs = [
    { id: 'campus_ia_training', label: 'Campus IA Training' },
    { id: 'nodo_inferencia_edge', label: 'Nodos Inferencia / Edge' },
    { id: 'benchmark_cabase', label: 'Benchmark CABASE' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-xs font-bold tracking-widest text-accent-cyan uppercase mb-1.5">
            Inteligencia Territorial / 05
          </div>
          <h1 className="text-3xl font-extrabold font-display text-editorial-dark tracking-tight">
            Cada provincia, en detalle
          </h1>
          <p className="text-sm font-medium text-editorial-muted mt-1 max-w-2xl">
            Compará el desempeño provincial en las seis dimensiones auditadas, su arquetipo K-Means y estabilidad Monte Carlo.
          </p>
        </div>

        {/* Profile Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-canvas-card rounded-xl border border-editorial-border shadow-xs">
          {perfilesTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => changePerfil(tab.id)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                activePerfil === tab.id
                  ? 'bg-[#1E293B] text-accent-cyan border border-accent-cyan/40 shadow-xs'
                  : 'text-editorial-muted hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Control Filter Bar */}
      <div className="bg-canvas-card rounded-2xl p-4 border border-editorial-border shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-editorial-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Buscar por provincia o región..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-canvas border border-editorial-border text-xs font-medium text-white placeholder:text-editorial-muted focus:outline-none focus:ring-1 focus:ring-accent-cyan"
          />
          {searchTerm && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-accent-cyan font-mono">
              {filteredAndSortedRows.length} encontradas
            </span>
          )}
        </div>

        {/* Sorting Dropdown & Reset */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-editorial-muted">Orden:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas border border-editorial-border text-white focus:outline-none focus:ring-1 focus:ring-accent-cyan"
            >
              <option value="score_desc">Mayor puntaje total ↓</option>
              <option value="score_asc">Menor puntaje total ↑</option>
              <option value="nombre_asc">Alfabético (A–Z)</option>
              <option value="prob_top3">Mayor estabilidad Monte Carlo (Prob. Top 3)</option>
              <option value="dim_subscore_energia">Mayor Energía ↓</option>
              <option value="dim_subscore_clima">Mayor Clima (PUE) ↓</option>
              <option value="dim_subscore_conectividad">Mayor Conectividad ↓</option>
              <option value="dim_subscore_fiscal">Mayor Fiscal / RIGI ↓</option>
              <option value="dim_subscore_talento_riesgo">Mayor Talento STEM ↓</option>
              <option value="dim_subscore_tier_readiness">Mayor Tier-Readiness ↓</option>
            </select>
          </div>

          <button
            onClick={resetFilters}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-canvas text-xs font-bold text-editorial-muted hover:text-white border border-editorial-border hover:bg-canvas-muted transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restablecer</span>
          </button>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-canvas-card rounded-2xl border border-editorial-border shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-canvas/90 border-b border-editorial-border text-editorial-muted uppercase tracking-wider text-[10px] font-bold select-none">
                <th className="py-3 px-3 text-center">#</th>
                <th className="py-3 px-4">Provincia</th>
                {DIMENSION_COLS.map((dim) => (
                  <th key={dim.id} className="py-3 px-2.5 text-center">
                    {dim.short}
                  </th>
                ))}
                <th className="py-3 px-3 text-right">Puntaje</th>
                <th className="py-3 px-3 text-center">Arquetipo K-Means</th>
                <th className="py-3 px-3 text-center">Estabilidad MC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-editorial-border/40">
              {filteredAndSortedRows.map((row, idx) => {
                const puesto = idx + 1;
                return (
                  <tr
                    key={row.id}
                    onClick={() => setSelectedProvinceId(row.id)}
                    className="hover:bg-canvas/60 transition-colors cursor-pointer group"
                  >
                    {/* Posición */}
                    <td className="py-3 px-3 text-center font-mono text-[11px] font-bold text-editorial-muted group-hover:text-accent-cyan">
                      {String(puesto).padStart(2, '0')}
                    </td>

                    {/* Nombre y Región */}
                    <td className="py-3 px-4">
                      <div className="font-bold text-white text-xs group-hover:text-accent-cyan transition-colors">
                        {row.nombre}
                      </div>
                      <div className="text-[10px] text-editorial-muted font-normal">
                        {row.region}
                      </div>
                    </td>

                    {/* 6 Subscores Heatmap Cells */}
                    {DIMENSION_COLS.map((dim) => {
                      const val = Math.round(row.subscores[dim.id] || 0);
                      const heatClass = getHeatmapClass(val);
                      return (
                        <td key={dim.id} className="py-2.5 px-2 text-center">
                          <span
                            className={`inline-block w-11 py-1 rounded-md text-[11px] font-mono font-bold tabular-nums ${heatClass}`}
                          >
                            {val}
                          </span>
                        </td>
                      );
                    })}

                    {/* Puntaje Total */}
                    <td className="py-3 px-3 text-right">
                      <div className="font-black text-white text-sm tabular-nums font-display">
                        {row.score}
                      </div>
                      <div className="w-16 ml-auto bg-canvas rounded-full h-1 mt-1 overflow-hidden">
                        <div
                          className="bg-accent-cyan h-1 rounded-full"
                          style={{ width: `${Math.min(row.score, 100)}%` }}
                        />
                      </div>
                    </td>

                    {/* Arquetipo K-Means */}
                    <td className="py-3 px-3 text-center">
                      <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium bg-canvas border border-editorial-border text-editorial-subtitle truncate max-w-[130px]">
                        {row.cluster}
                      </span>
                    </td>

                    {/* Estabilidad Monte Carlo */}
                    <td className="py-3 px-3 text-center">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tabular-nums border ${
                          row.probTop3 >= 75
                            ? 'bg-emerald-950/40 text-accent-emerald border-emerald-800'
                            : row.probTop3 >= 25
                            ? 'bg-indigo-950/40 text-accent-cyan border-indigo-800'
                            : 'bg-canvas text-editorial-muted border-editorial-border'
                        }`}
                      >
                        {row.probTop3 > 0 ? `${row.probTop3.toFixed(0)}% Top 3` : '0%'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Heatmap Legend Bar */}
        <div className="p-4 bg-canvas/90 border-t border-editorial-border flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-editorial-muted">
          <div className="flex items-center gap-6 flex-wrap">
            <span className="font-bold text-white text-[11px] uppercase tracking-wider">
              Referencias de Desempeño:
            </span>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-[#132B24] border border-[#1A5336]" />
              <span className="font-medium text-white">80–100 · Alto</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-[#132338] border border-[#1D4063]" />
              <span className="font-medium text-white">60–79 · Medio</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-[#33171D] border border-[#5E1E26]" />
              <span className="font-medium text-white">0–59 · Inicial</span>
            </div>
          </div>

          <span className="font-mono text-[11px]">
            {filteredAndSortedRows.length} de 24 jurisdicciones mostradas
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-bold tracking-wider uppercase text-editorial-muted">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Scores y probabilidades Monte Carlo extraídos de fact_scores_perfiles.csv auditado.
        </span>
      </div>
    </div>
  );
}
