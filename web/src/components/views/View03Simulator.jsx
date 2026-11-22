import React, { useState, useMemo } from 'react';
import { useAppData } from '../../context/DataContext';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { RotateCcw } from 'lucide-react';

const DIMENSIONS_ORDER = [
  { id: 'subscore_energia', key: 'dimension_energia', label: 'Energía' },
  { id: 'subscore_conectividad', key: 'dimension_conectividad', label: 'Conectividad' },
  { id: 'subscore_clima', key: 'dimension_clima', label: 'Clima' },
  { id: 'subscore_fiscal', key: 'dimension_fiscal', label: 'Fiscal / RIGI' },
  { id: 'subscore_talento_riesgo', key: 'dimension_talento_riesgo', label: 'Talento / Riesgo' },
  { id: 'subscore_tier_readiness', key: 'dimension_tier_readiness', label: 'Tier-Readiness' },
];

export default function View03Simulator() {
  const { data, selectedProvinceId, setSelectedProvinceId } = useAppData();

  // Pesos en porcentaje (0-100) que suman 100
  const [weights, setWeights] = useState({
    subscore_energia: 30,
    subscore_clima: 20,
    subscore_tier_readiness: 15,
    subscore_fiscal: 15,
    subscore_conectividad: 10,
    subscore_talento_riesgo: 10,
  });

  const [selectedProvId, setSelectedProvId] = useState(
    selectedProvinceId ? Number(selectedProvinceId) : 58
  );

  if (!data) return null;

  const { jurisdicciones, perfiles_config } = data;

  // Cargar preset predefinido
  const loadPreset = (presetKey) => {
    if (presetKey === 'campus_ia') {
      setWeights({
        subscore_energia: 30,
        subscore_clima: 20,
        subscore_tier_readiness: 15,
        subscore_fiscal: 15,
        subscore_conectividad: 10,
        subscore_talento_riesgo: 10,
      });
    } else if (presetKey === 'nodo_edge') {
      setWeights({
        subscore_conectividad: 30,
        subscore_talento_riesgo: 20,
        subscore_tier_readiness: 15,
        subscore_energia: 15,
        subscore_fiscal: 10,
        subscore_clima: 10,
      });
    } else if (presetKey === 'equilibrado') {
      setWeights({
        subscore_energia: 16.67,
        subscore_clima: 16.67,
        subscore_conectividad: 16.67,
        subscore_fiscal: 16.67,
        subscore_talento_riesgo: 16.66,
        subscore_tier_readiness: 16.66,
      });
    }
  };

  // Manejar cambio individual de slider con renormalización automática inteligente
  const handleSliderChange = (changedKey, newVal) => {
    const clampedNew = Math.max(0, Math.min(100, Number(newVal)));
    const otherKeys = DIMENSIONS_ORDER.map((d) => d.id).filter((k) => k !== changedKey);
    const otherSum = otherKeys.reduce((acc, k) => acc + (weights[k] || 0), 0);
    const targetRemainder = 100 - clampedNew;

    const newWeights = { ...weights, [changedKey]: clampedNew };

    if (otherSum === 0) {
      // Repartir equitativamente el resto
      const share = targetRemainder / otherKeys.length;
      otherKeys.forEach((k) => {
        newWeights[k] = Math.round(share * 10) / 10;
      });
    } else {
      // Repartir proporcionalmente
      const factor = targetRemainder / otherSum;
      otherKeys.forEach((k) => {
        newWeights[k] = Math.max(0, Math.round((weights[k] || 0) * factor * 10) / 10);
      });
    }

    setWeights(newWeights);
  };

  // Total acumulado
  const totalWeight = useMemo(() => {
    return Math.round(Object.values(weights).reduce((a, b) => a + b, 0));
  }, [weights]);

  // Recalcular scores de todas las 24 provincias según los pesos actuales
  const rankingSimulado = useMemo(() => {
    const totalW = Object.values(weights).reduce((a, b) => a + b, 0) || 1;
    return jurisdicciones
      .map((j) => {
        let score = 0;
        DIMENSIONS_ORDER.forEach((dim) => {
          const w = (weights[dim.id] || 0) / totalW;
          const sub = j.subscores?.[dim.id] || 0;
          score += sub * w;
        });
        const scoreRound = Math.round(score * 10) / 10;
        return {
          id: j.id,
          nombre: j.nombre,
          corta: j.corta || j.nombre,
          region: j.region,
          score: scoreRound,
          cluster: j.cluster?.nombre,
          subscores: j.subscores,
        };
      })
      .sort((a, b) => b.score - a.score)
      .map((j, idx) => ({ ...j, rank: idx + 1 }));
  }, [jurisdicciones, weights]);

  // Provincia actualmente seleccionada
  const activeProvince = useMemo(() => {
    return (
      rankingSimulado.find((j) => j.id === selectedProvId) || rankingSimulado[0]
    );
  }, [rankingSimulado, selectedProvId]);

  // Datos para el gráfico Radar (6 vértices)
  const radarData = useMemo(() => {
    if (!activeProvince) return [];
    return DIMENSIONS_ORDER.map((dim) => ({
      dimension: dim.label,
      valor: Math.round(activeProvince.subscores?.[dim.id] || 0),
      fullMark: 100,
    }));
  }, [activeProvince]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-xs font-bold tracking-widest text-accent-indigo uppercase mb-1.5">
            Inteligencia Territorial / 03
          </div>
          <h1 className="text-3xl font-extrabold text-editorial-dark tracking-tight">
            Diseñá tu escenario ideal
          </h1>
          <p className="text-sm text-editorial-muted mt-1 max-w-2xl">
            Ajustá la importancia de cada variable y compará el potencial provincial.
          </p>
        </div>

        {/* Preset quick buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-white/70 backdrop-blur-xs rounded-xl border border-editorial-border shadow-2xs">
          <span className="text-[11px] font-semibold text-editorial-muted px-2">
            Presets:
          </span>
          <button
            onClick={() => loadPreset('campus_ia')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium hover:bg-canvas text-editorial-dark transition-all"
          >
            Campus IA
          </button>
          <button
            onClick={() => loadPreset('nodo_edge')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium hover:bg-canvas text-editorial-dark transition-all"
          >
            Nodos Edge
          </button>
          <button
            onClick={() => loadPreset('equilibrado')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium hover:bg-canvas text-editorial-dark transition-all"
          >
            Equilibrado
          </button>
        </div>
      </div>

      {/* Grid: Prioridades Sliders (1.2/3) + Espectro de Viabilidad Radar (1.8/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left Column: Sliders (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-base font-bold text-editorial-dark">
                Configurá tus prioridades
              </h2>
              <button
                onClick={() => loadPreset('equilibrado')}
                title="Restablecer pesos a valores equilibrados"
                className="text-editorial-muted hover:text-editorial-dark transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-xs text-editorial-muted mb-5">
              Peso de cada dimensión en el puntaje final
            </p>

            {/* 6 Sliders */}
            <div className="space-y-4">
              {DIMENSIONS_ORDER.map((dim) => {
                const w = Math.round(weights[dim.id] || 0);
                return (
                  <div key={dim.id}>
                    <div className="flex justify-between items-center text-xs mb-1.5">
                      <span className="font-medium text-editorial-dark">{dim.label}</span>
                      <span className="font-bold text-editorial-dark tabular-nums">{w}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={w}
                      onChange={(e) => handleSliderChange(dim.id, e.target.value)}
                      className="w-full accent-editorial-dark cursor-pointer h-1.5 bg-canvas rounded-lg"
                    />
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-editorial-border/60 flex items-center justify-between text-xs">
            <span className="font-medium text-editorial-muted">Peso total configurado</span>
            <span
              className={`px-3 py-1 rounded-full font-bold tabular-nums ${
                totalWeight === 100
                  ? 'bg-accent-sageSoft text-accent-sageDark'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              {totalWeight}%
            </span>
          </div>
        </div>

        {/* Right Column: Espectro de Viabilidad Radar + Score Card (3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
              <div>
                <h2 className="text-base font-bold text-editorial-dark">
                  Espectro de viabilidad
                </h2>
                <p className="text-xs text-editorial-muted">
                  Puntos por dimensión · escala de 0 a 100
                </p>
              </div>

              {/* Selector de provincia */}
              <select
                value={selectedProvId}
                onChange={(e) => {
                  const id = Number(e.target.value);
                  setSelectedProvId(id);
                  setSelectedProvinceId(id);
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-canvas border border-editorial-border text-editorial-dark focus:outline-none"
              >
                {jurisdicciones.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Radar and Score Banner */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center mt-3">
              {/* Radar Recharts (2 cols) */}
              <div className="md:col-span-2 h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                    <PolarGrid stroke="#e4e1d7" strokeDasharray="3 3" />
                    <PolarAngleAxis
                      dataKey="dimension"
                      tick={{ fill: '#4a3d46', fontSize: 11, fontWeight: 500 }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      ticks={[25, 50, 75, 100]}
                      tick={{ fill: '#a0999e', fontSize: 9 }}
                      axisLine={false}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const item = payload[0].payload;
                          return (
                            <div className="bg-sidebar-bg text-white px-2.5 py-1.5 rounded-lg text-xs shadow-md border border-sidebar-border">
                              <span className="font-semibold">{item.dimension}: </span>
                              <span className="font-bold text-accent-sage">{item.valor}/100</span>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Radar
                      name="Subscore"
                      dataKey="valor"
                      stroke="#4c35de"
                      fill="#4c35de"
                      fillOpacity={0.45}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* Score Highlight Box (1 col) */}
              <div className="bg-accent-sageSoft/70 rounded-2xl p-5 border border-accent-sage/30 flex flex-col justify-between h-56">
                <div>
                  <span className="text-[10px] font-bold tracking-widest uppercase text-editorial-muted block mb-1">
                    Puntaje final
                  </span>
                  <div className="flex items-baseline gap-1 my-1">
                    <span className="text-4xl font-black text-editorial-dark">
                      {Math.round(activeProvince?.score || 0)}
                    </span>
                    <span className="text-xs font-semibold text-editorial-muted">/100</span>
                  </div>
                  <div className="mt-3">
                    <span className="text-xs font-bold text-editorial-dark block">
                      {activeProvince?.rank ? `${String(activeProvince.rank).padStart(2, '0')} en el ranking` : '-'}
                    </span>
                    <span className="text-[11px] text-editorial-muted">
                      {activeProvince?.region}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-accent-sage/40">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white text-accent-sageDark border border-accent-sage/40">
                    Escenario en vivo
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-editorial-border/60 text-[11px] text-editorial-muted">
            Fórmula en vivo: Puntaje = ∑ (Subscore_i × Peso_i) / 100
          </div>
        </div>
      </div>

      {/* Bottom Table: Ranking Provincial Dinámico */}
      <div className="bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-editorial-dark">
              Ranking provincial recalculado en vivo
            </h2>
            <p className="text-xs text-editorial-muted">
              Orden de viabilidad para las 24 jurisdicciones según las prioridades configuradas.
            </p>
          </div>
          <span className="text-xs font-medium text-editorial-muted">
            24 jurisdicciones evaluadas
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-editorial-border/70 text-editorial-muted uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Posición</th>
                <th className="py-2.5 px-3">Provincia</th>
                <th className="py-2.5 px-3 w-1/3">Índice de viabilidad</th>
                <th className="py-2.5 px-3 text-right">Puntaje</th>
                <th className="py-2.5 px-3 text-center">Nivel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-editorial-border/40">
              {rankingSimulado.slice(0, 10).map((prov) => {
                const isSelected = prov.id === selectedProvId;
                const nivel =
                  prov.score >= 80 ? 'Alta' : prov.score >= 65 ? 'Media' : 'Inicial';
                const pillClass =
                  nivel === 'Alta'
                    ? 'bg-heatmap-highBg text-heatmap-highText'
                    : nivel === 'Media'
                    ? 'bg-heatmap-medBg text-heatmap-medText'
                    : 'bg-heatmap-lowBg text-heatmap-lowText';

                return (
                  <tr
                    key={prov.id}
                    onClick={() => {
                      setSelectedProvId(prov.id);
                      setSelectedProvinceId(prov.id);
                    }}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-accent-sageSoft/40 font-semibold'
                        : 'hover:bg-canvas/50'
                    }`}
                  >
                    <td className="py-2.5 px-3 text-editorial-muted font-mono">
                      {String(prov.rank).padStart(2, '0')}
                    </td>
                    <td className="py-2.5 px-3 font-medium text-editorial-dark">
                      {prov.nombre}
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="w-full bg-canvas rounded-full h-2 overflow-hidden">
                        <div
                          className="h-2 rounded-full transition-all duration-300"
                          style={{
                            width: `${Math.min(prov.score, 100)}%`,
                            backgroundColor: isSelected ? '#181829' : '#8fa8a2',
                          }}
                        />
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-editorial-dark tabular-nums">
                      {prov.score} /100
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${pillClass}`}>
                        {nivel}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
