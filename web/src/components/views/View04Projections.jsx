import React, { useState, useMemo } from 'react';
import { useAppData } from '../../context/DataContext';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { TrendingUp, Calendar, Zap, ArrowUp, ArrowDown } from 'lucide-react';

const ESCENARIOS_CONFIG = {
  acelerado: {
    label: 'Acelerado',
    color: '#38BDF8', // Cian brillante
    strokeDash: '0',
    desc: 'Expansión energética y de redes con inversión sostenida en infraestructura digital e incentivos RIGI plenamente operativos.',
    bgCard: 'bg-[#101E33]',
    borderCard: 'border-accent-cyan/40',
    badgeText: 'text-accent-cyan'
  },
  tendencial: {
    label: 'Tendencial',
    color: '#818CF8', // Índigo/púrpura suave
    strokeDash: '0',
    desc: 'Mejoras graduales de capacidad y continuidad en los planes de inversión pública y privada actuales sin shocks exógenos.',
    bgCard: 'bg-[#141A2D]',
    borderCard: 'border-indigo-800/40',
    badgeText: 'text-indigo-400'
  },
  conservador: {
    label: 'Conservador',
    color: '#94A3B8', // Pizarra / Gris
    strokeDash: '4 4',
    desc: 'Avance limitado por restricciones macroeconómicas, cuellos de botella en transporte eléctrico y desaceleración de obra.',
    bgCard: 'bg-[#131724]',
    borderCard: 'border-editorial-border',
    badgeText: 'text-slate-400'
  }
};

export default function View04Projections() {
  const { data, activePerfil, changePerfil, selectedProvinceId, setSelectedProvinceId } = useAppData();

  const [selectedHorizon, setSelectedHorizon] = useState('2026-2036');

  if (!data) return null;

  const { jurisdicciones, proyecciones } = data;

  const activeProvId = selectedProvinceId ? String(selectedProvinceId) : '58';
  const activeProvince = jurisdicciones.find((j) => String(j.id) === activeProvId) || jurisdicciones[0];

  // Determinar año final según horizonte
  const maxAnio = selectedHorizon === '2026-2028' ? 2028 : selectedHorizon === '2026-2031' ? 2031 : 2036;

  // Extraer series temporales para la provincia y perfil seleccionados
  const provProyecciones = proyecciones?.[activePerfil]?.[activeProvId] || {};

  // Formatear datos para Recharts combinando los 3 escenarios por año
  const chartData = useMemo(() => {
    const acel = provProyecciones.acelerado || [];
    const tend = provProyecciones.tendencial || [];
    const cons = provProyecciones.conservador || [];

    const aniosMap = {};

    acel.forEach((p) => {
      if (p.anio <= maxAnio) {
        aniosMap[p.anio] = { anio: p.anio, Acelerado: p.score, deltaAcel: p.delta_score_vs_2026 };
      }
    });

    tend.forEach((p) => {
      if (p.anio <= maxAnio && aniosMap[p.anio]) {
        aniosMap[p.anio].Tendencial = p.score;
        aniosMap[p.anio].deltaTend = p.delta_score_vs_2026;
      }
    });

    cons.forEach((p) => {
      if (p.anio <= maxAnio && aniosMap[p.anio]) {
        aniosMap[p.anio].Conservador = p.score;
        aniosMap[p.anio].deltaCons = p.delta_score_vs_2026;
      }
    });

    return Object.values(aniosMap).sort((a, b) => a.anio - b.anio);
  }, [provProyecciones, maxAnio]);

  // Extraer valores finales para las tarjetas inferiores
  const finalValues = useMemo(() => {
    const lastItem = chartData[chartData.length - 1] || {};
    const firstItem = chartData[0] || {};
    return {
      anioFinal: lastItem.anio || maxAnio,
      baseScore: firstItem.Acelerado || 0,
      acel: {
        score: lastItem.Acelerado || 0,
        delta: lastItem.deltaAcel || 0,
      },
      tend: {
        score: lastItem.Tendencial || 0,
        delta: lastItem.deltaTend || 0,
      },
      cons: {
        score: lastItem.Conservador || 0,
        delta: lastItem.deltaCons || 0,
      }
    };
  }, [chartData, maxAnio]);

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
            Inteligencia Territorial / 04
          </div>
          <h1 className="text-3xl font-extrabold font-display text-editorial-dark tracking-tight">
            Una mirada hacia el futuro
          </h1>
          <p className="text-sm font-medium text-editorial-muted mt-1 max-w-2xl">
            Compará la evolución del índice de viabilidad bajo tres escenarios predictivos de desarrollo hacia 2036.
          </p>
        </div>

        {/* Profile Switcher Pills */}
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

      {/* Main Graph Card */}
      <div className="bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs">
        {/* Graph Header and Selectors */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-4 border-b border-editorial-border">
          <div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-accent-cyan" />
              <h2 className="text-base font-bold font-display text-white">
                Evolución proyectada del índice
              </h2>
            </div>
            <p className="text-xs text-editorial-muted mt-0.5 font-medium">
              {activeProvince.nombre} ({activeProvince.region}) · Puntaje de viabilidad proyectado sobre 100
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Province Selector */}
            <select
              value={activeProvId}
              onChange={(e) => setSelectedProvinceId(Number(e.target.value))}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas border border-editorial-border text-white focus:outline-none focus:ring-1 focus:ring-accent-cyan"
            >
              {jurisdicciones.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.nombre}
                </option>
              ))}
            </select>

            {/* Horizon Selector */}
            <select
              value={selectedHorizon}
              onChange={(e) => setSelectedHorizon(e.target.value)}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas border border-editorial-border text-accent-cyan focus:outline-none focus:ring-1 focus:ring-accent-cyan font-mono"
            >
              <option value="2026-2028">Horizonte 2026–2028</option>
              <option value="2026-2031">Horizonte 2026–2031</option>
              <option value="2026-2036">Horizonte 2026–2036</option>
            </select>
          </div>
        </div>

        {/* Line Chart Viewport */}
        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 15, right: 25, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E2538" />
              <XAxis 
                dataKey="anio" 
                tick={{ fill: '#CBD5E1', fontSize: 11, fontWeight: 600 }} 
                axisLine={{ stroke: '#232B3E' }} 
                tickLine={false} 
              />
              <YAxis 
                domain={['auto', 'auto']} 
                tick={{ fill: '#64748B', fontSize: 11 }} 
                axisLine={{ stroke: '#232B3E' }} 
                tickLine={false} 
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-sidebar-bg text-white px-3.5 py-2.5 rounded-xl text-xs shadow-xl border border-editorial-border space-y-1.5">
                        <p className="font-bold text-accent-cyan font-mono">Año {label}</p>
                        {payload.map((entry, index) => (
                          <div key={index} className="flex items-center justify-between gap-4">
                            <span className="flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                              <span className="text-editorial-muted">{entry.name}:</span>
                            </span>
                            <span className="font-bold tabular-nums text-white">{entry.value} pts</span>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px', paddingTop: '15px' }} 
                iconType="plainline" 
              />
              <Line
                type="monotone"
                dataKey="Acelerado"
                stroke={ESCENARIOS_CONFIG.acelerado.color}
                strokeWidth={3}
                dot={{ r: 4, fill: ESCENARIOS_CONFIG.acelerado.color }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="Tendencial"
                stroke={ESCENARIOS_CONFIG.tendencial.color}
                strokeWidth={2.2}
                dot={{ r: 3.5, fill: ESCENARIOS_CONFIG.tendencial.color }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="Conservador"
                stroke={ESCENARIOS_CONFIG.conservador.color}
                strokeWidth={1.8}
                strokeDasharray="4 4"
                dot={{ r: 3, fill: ESCENARIOS_CONFIG.conservador.color }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="pt-3 border-t border-editorial-border text-[11px] text-editorial-muted flex items-center justify-between">
          <span>Punto de partida común: <strong className="text-white tabular-nums">{finalValues.baseScore} pts</strong> (Base 2026)</span>
          <span>Modelo de proyección multivariada validado con Monte Carlo</span>
        </div>
      </div>

      {/* 3 Bottom Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Acelerado */}
        <div className={`${ESCENARIOS_CONFIG.acelerado.bgCard} rounded-2xl p-6 border ${ESCENARIOS_CONFIG.acelerado.borderCard} shadow-xs flex flex-col justify-between`}>
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-accent-cyan" />
                <h3 className="text-sm font-bold text-white">Escenario Acelerado</h3>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30">
                Inversión alta
              </span>
            </div>

            <div className="my-3">
              <div className="flex items-baseline gap-1.5">
                <span className="text-4xl font-black font-display text-white tabular-nums">
                  {finalValues.acel.score}
                </span>
                <span className="text-xs font-semibold text-editorial-muted">pts en {finalValues.anioFinal}</span>
              </div>
              <div className="mt-1 flex items-center gap-1 text-xs font-bold text-accent-emerald">
                <ArrowUp className="w-3.5 h-3.5" />
                <span>+{finalValues.acel.delta.toFixed(1)} puntos vs. 2026</span>
              </div>
            </div>

            <p className="text-xs text-editorial-body leading-relaxed mt-3">
              {ESCENARIOS_CONFIG.acelerado.desc}
            </p>
          </div>
        </div>

        {/* Card 2: Tendencial */}
        <div className={`${ESCENARIOS_CONFIG.tendencial.bgCard} rounded-2xl p-6 border ${ESCENARIOS_CONFIG.tendencial.borderCard} shadow-xs flex flex-col justify-between`}>
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400" />
                <h3 className="text-sm font-bold text-white">Escenario Tendencial</h3>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                Línea base
              </span>
            </div>

            <div className="my-3">
              <div className="flex items-baseline gap-1.5">
                <span className="text-4xl font-black font-display text-white tabular-nums">
                  {finalValues.tend.score}
                </span>
                <span className="text-xs font-semibold text-editorial-muted">pts en {finalValues.anioFinal}</span>
              </div>
              <div className="mt-1 flex items-center gap-1 text-xs font-bold text-accent-cyan">
                <ArrowUp className="w-3.5 h-3.5" />
                <span>+{finalValues.tend.delta.toFixed(1)} puntos vs. 2026</span>
              </div>
            </div>

            <p className="text-xs text-editorial-body leading-relaxed mt-3">
              {ESCENARIOS_CONFIG.tendencial.desc}
            </p>
          </div>
        </div>

        {/* Card 3: Conservador */}
        <div className={`${ESCENARIOS_CONFIG.conservador.bgCard} rounded-2xl p-6 border ${ESCENARIOS_CONFIG.conservador.borderCard} shadow-xs flex flex-col justify-between`}>
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
                <h3 className="text-sm font-bold text-white">Escenario Conservador</h3>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-slate-700">
                Inversión baja
              </span>
            </div>

            <div className="my-3">
              <div className="flex items-baseline gap-1.5">
                <span className="text-4xl font-black font-display text-white tabular-nums">
                  {finalValues.cons.score}
                </span>
                <span className="text-xs font-semibold text-editorial-muted">pts en {finalValues.anioFinal}</span>
              </div>
              <div className="mt-1 flex items-center gap-1 text-xs font-semibold text-slate-400">
                <span>{finalValues.cons.delta >= 0 ? `+${finalValues.cons.delta.toFixed(1)}` : finalValues.cons.delta.toFixed(1)} puntos vs. 2026</span>
              </div>
            </div>

            <p className="text-xs text-editorial-body leading-relaxed mt-3">
              {ESCENARIOS_CONFIG.conservador.desc}
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-bold tracking-wider uppercase text-editorial-muted">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Series temporales generadas mediante el motor predictivo validado en fact_proyecciones_2026_2036.csv.
        </span>
      </div>
    </div>
  );
}
