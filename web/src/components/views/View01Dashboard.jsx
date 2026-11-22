import React from 'react';
import { useAppData } from '../../context/DataContext';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ArrowRight, Zap, Thermometer, Network, Scale, ShieldCheck, Server } from 'lucide-react';

const DIMENSION_ICONS = {
  subscore_energia: Zap,
  subscore_clima: Thermometer,
  subscore_conectividad: Network,
  subscore_fiscal: Scale,
  subscore_talento_riesgo: ShieldCheck,
  subscore_tier_readiness: Server
};

export default function View01Dashboard({ onNavigate }) {
  const { data, activePerfil, changePerfil } = useAppData();

  if (!data) return null;

  const kpis = data.kpis_por_perfil?.[activePerfil] || {};
  const perfilesConfig = data.perfiles_config || {};

  // Ranking ordenado completo con etiquetas abreviadas legibles para el eje X
  const rankedProvinces = [...data.jurisdicciones]
    .map((j) => {
      const pData = j.scores_perfiles?.[activePerfil] || {};
      const shortName = j.corta || j.nombre;
      let displayName = shortName;
      if (shortName === 'Ciudad Autónoma de Buenos Aires' || shortName.includes('Autónoma')) {
        displayName = 'CABA';
      } else if (shortName === 'Tierra del Fuego') {
        displayName = 'T. del Fuego';
      } else if (shortName === 'Santiago del Estero') {
        displayName = 'Stgo. Estero';
      }

      return {
        id: j.id,
        nombre: displayName,
        nombreCompleto: j.nombre,
        score: pData.score_base || 0,
        rank: pData.rank_base || 99,
        region: j.region
      };
    })
    .sort((a, b) => b.score - a.score);

  // Top 10 Provincias solicitado
  const top10 = rankedProvinces.slice(0, 10);

  // Selector de perfiles
  const perfilesTabs = [
    { id: 'campus_ia_training', label: 'Campus IA Training' },
    { id: 'nodo_inferencia_edge', label: 'Nodos Inferencia / Edge' },
    { id: 'benchmark_cabase', label: 'Benchmark CABASE' },
  ];

  return (
    <div className="space-y-7 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header and Profile Switcher */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-xs font-bold tracking-widest text-accent-cyan uppercase mb-1.5">
            Inteligencia Territorial / 01
          </div>
          <h1 className="text-3xl font-extrabold font-display text-editorial-dark tracking-tight">
            Viabilidad IA data center
          </h1>
          <p className="text-sm font-medium text-editorial-muted mt-1 max-w-2xl">
            Una visión integral del potencial de Argentina para infraestructura de inteligencia artificial.
          </p>
        </div>

        {/* Profile Selector Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-canvas-card rounded-xl border border-editorial-border shadow-xs">
          {perfilesTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => changePerfil(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activePerfil === tab.id
                  ? 'bg-[#1E293B] text-accent-cyan font-bold border border-accent-cyan/40 shadow-xs'
                  : 'text-editorial-muted hover:text-editorial-subtitle hover:bg-canvas-muted'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 5 KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* KPI 1: Cobertura */}
        <div className="bg-canvas-card rounded-2xl p-5 border border-editorial-border shadow-xs flex flex-col justify-between">
          <span className="text-xs font-bold text-editorial-muted uppercase tracking-wider">Provincias evaluadas</span>
          <div className="my-2">
            <span className="text-3xl font-black font-display text-editorial-dark tabular-nums">24</span>
          </div>
          <span className="text-[11px] font-medium text-editorial-muted">Cobertura nacional total</span>
        </div>

        {/* KPI 2: Mayor Viabilidad (Destacada en Azul Nocturno / Cian) */}
        <div className="bg-[#10192A] text-white rounded-2xl p-5 border border-accent-cyan/40 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-accent-cyan uppercase tracking-wider">Mayor viabilidad</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black font-display text-white tabular-nums">{kpis.top1_score || 0}</span>
            <span className="text-sm text-accent-cyan font-bold">/100</span>
          </div>
          <span className="text-[11px] text-editorial-subtitle font-bold truncate">
            {kpis.top1_nombre} lidera el índice
          </span>
        </div>

        {/* KPI 3: Energía Máximo */}
        <div className="bg-canvas-card rounded-2xl p-5 border border-editorial-border shadow-xs flex flex-col justify-between">
          <span className="text-xs font-bold text-editorial-muted uppercase tracking-wider">Energía · máximo</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black font-display text-accent-amber tabular-nums">{Math.round(kpis.max_energia_score || 0)}</span>
            <span className="text-sm text-editorial-muted font-bold">/100</span>
          </div>
          <span className="text-[11px] font-bold text-editorial-subtitle truncate">{kpis.max_energia_provincia}</span>
        </div>

        {/* KPI 4: Conectividad Máximo */}
        <div className="bg-canvas-card rounded-2xl p-5 border border-editorial-border shadow-xs flex flex-col justify-between">
          <span className="text-xs font-bold text-editorial-muted uppercase tracking-wider">Conectividad · máximo</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black font-display text-accent-cyan tabular-nums">{Math.round(kpis.max_conectividad_score || 0)}</span>
            <span className="text-sm text-editorial-muted font-bold">/100</span>
          </div>
          <span className="text-[11px] font-bold text-editorial-subtitle truncate">{kpis.max_conectividad_provincia}</span>
        </div>

        {/* KPI 5: Dimensiones */}
        <div className="bg-canvas-card rounded-2xl p-5 border border-editorial-border shadow-xs flex flex-col justify-between">
          <span className="text-xs font-bold text-editorial-muted uppercase tracking-wider">Dimensiones del modelo</span>
          <div className="my-2">
            <span className="text-3xl font-black font-display text-accent-emerald tabular-nums">6</span>
          </div>
          <span className="text-[11px] font-medium text-editorial-muted">Ponderación MCDA auditada</span>
        </div>
      </div>

      {/* Middle Section: Top 10 Bar Chart (2/3) + Lectura del Territorio (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 10 Bar Chart */}
        <div className="lg:col-span-2 bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-base font-bold font-display text-editorial-dark">
                Las provincias mejor posicionadas
              </h2>
              <span className="text-xs font-semibold text-accent-cyan bg-canvas px-2.5 py-0.5 rounded-full border border-editorial-border">
                Top 10 nacional
              </span>
            </div>
            <p className="text-xs text-editorial-muted mb-4 font-medium">
              Índice compuesto de viabilidad · escala de 0 a 100
            </p>

            <div className="w-full min-w-0">
              <ResponsiveContainer width="100%" height={340}>
                <BarChart data={top10} margin={{ top: 15, right: 15, left: -15, bottom: 35 }}>
                  <XAxis 
                    dataKey="nombre" 
                    tick={{ fill: '#E2E8F0', fontSize: 11, fontWeight: 600 }} 
                    axisLine={{ stroke: '#94A3B8' }} 
                    tickLine={{ stroke: '#94A3B8' }} 
                    angle={-25}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis 
                    domain={[0, 100]} 
                    ticks={[0, 25, 50, 75, 100]} 
                    tick={{ fill: '#94A3B8', fontSize: 11, fontWeight: 500 }} 
                    axisLine={{ stroke: '#94A3B8' }} 
                    tickLine={{ stroke: '#94A3B8' }} 
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const item = payload[0].payload;
                        return (
                          <div className="bg-[#0B0E17] text-white px-3.5 py-2.5 rounded-xl text-xs shadow-2xl border border-editorial-border/80">
                            <p className="font-bold text-white text-sm mb-1">{item.nombreCompleto}</p>
                            <p className="text-slate-300 font-medium">
                              Índice de viabilidad: <span className="font-black text-accent-cyan tabular-nums text-sm">{item.score}</span> / 100
                            </p>
                            <p className="text-slate-400 text-[11px] mt-0.5">Puesto #{item.rank} nacional</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                    {top10.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={index === 0 ? '#38BDF8' : index < 3 ? '#2563EB' : '#334155'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 border-t border-editorial-border text-[11px] text-editorial-muted flex justify-between items-center">
            <span>Ponderación oficial: <strong className="text-editorial-subtitle">{perfilesConfig[activePerfil]?._nombre || activePerfil}</strong></span>
            <button 
              onClick={() => onNavigate && onNavigate('matrix')}
              className="text-accent-cyan hover:text-accent-cyan/80 font-bold hover:underline"
            >
              Ver las 24 provincias →
            </button>
          </div>
        </div>

        {/* Lectura del Territorio (Editorial Box) */}
        <div className="bg-[#10192A] rounded-2xl p-6 border border-accent-cyan/30 flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold tracking-widest text-accent-cyan uppercase mb-3">
              Lectura del territorio
            </div>
            <h3 className="text-2xl font-black font-display text-white tracking-tight leading-tight mb-4">
              {kpis.lectura_editorial?.titulo || 'La energía abre la oportunidad.'}
            </h3>
            <p className="text-sm text-editorial-body leading-relaxed mb-6 font-normal">
              {kpis.lectura_editorial?.cuerpo}
            </p>

            <div className="pt-4 border-t border-editorial-border">
              <h4 className="text-xs font-bold text-white mb-1">
                El equilibrio importa
              </h4>
              <p className="text-xs text-editorial-body leading-relaxed">
                {kpis.lectura_editorial?.equilibrio}
              </p>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={() => onNavigate && onNavigate('simulator')}
              className="inline-flex items-center gap-2 text-sm font-bold text-accent-cyan hover:text-white transition-colors group"
            >
              <span>Explorá las variables en el simulador</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Section: Un índice, seis perspectivas */}
      <div className="bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs">
        <div className="mb-4">
          <h2 className="text-base font-bold font-display text-editorial-dark">
            Un índice, seis perspectivas
          </h2>
          <p className="text-xs text-editorial-muted font-medium">
            Macro-dimensiones analíticas auditadas del modelo multicriterio (MCDA).
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
          {data.dimensiones.map((dim) => {
            const Icon = DIMENSION_ICONS[dim.id] || Zap;
            const weightPct = perfilesConfig[activePerfil]?.[dim.key] 
              ? Math.round(perfilesConfig[activePerfil][dim.key] * 100) 
              : 0;

            return (
              <div 
                key={dim.id} 
                className="p-4 rounded-xl bg-canvas/60 border border-editorial-border flex flex-col justify-between hover:bg-canvas transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold font-mono text-accent-cyan">
                      {dim.codigo}
                    </span>
                    <Icon className="w-4 h-4 text-editorial-subtitle" />
                  </div>
                  <h3 className="text-sm font-bold text-editorial-dark mb-1">
                    {dim.nombre}
                  </h3>
                  <p className="text-xs text-editorial-body line-clamp-3 leading-snug">
                    {dim.descripcion}
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-editorial-border/60 text-[11px] text-editorial-muted flex justify-between font-medium">
                  <span>Peso perfil:</span>
                  <strong className="text-white tabular-nums">{weightPct}%</strong>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Disclaimer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-bold tracking-wider uppercase text-editorial-muted">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Modelo auditado con fuentes públicas oficiales. Datos trazables a través de data_freshness.json.
        </span>
      </div>
    </div>
  );
}
