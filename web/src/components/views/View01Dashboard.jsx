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

  // Calcular ranking ordenado para el perfil activo
  const rankedProvinces = [...data.jurisdicciones]
    .map((j) => {
      const pData = j.scores_perfiles?.[activePerfil] || {};
      return {
        id: j.id,
        nombre: j.corta || j.nombre,
        nombreCompleto: j.nombre,
        score: pData.score_base || 0,
        rank: pData.rank_base || 99,
        region: j.region
      };
    })
    .sort((a, b) => b.score - a.score);

  const top6 = rankedProvinces.slice(0, 6);

  // Perfiles selector tabs
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
          <div className="text-xs font-bold tracking-widest text-accent-indigo uppercase mb-1.5">
            Inteligencia Territorial / 01
          </div>
          <h1 className="text-3xl font-extrabold text-editorial-dark tracking-tight">
            Viabilidad IA data center
          </h1>
          <p className="text-sm text-editorial-muted mt-1 max-w-2xl">
            Una visión integral del potencial de Argentina para infraestructura de inteligencia artificial.
          </p>
        </div>

        {/* Profile Selector Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-white/70 backdrop-blur-xs rounded-xl border border-editorial-border shadow-2xs">
          {perfilesTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => changePerfil(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activePerfil === tab.id
                  ? 'bg-editorial-dark text-white shadow-xs'
                  : 'text-editorial-muted hover:text-editorial-dark hover:bg-canvas-muted/50'
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
        <div className="bg-white rounded-2xl p-5 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <span className="text-xs font-medium text-editorial-muted">Provincias evaluadas</span>
          <div className="my-2">
            <span className="text-3xl font-black text-editorial-dark">24</span>
          </div>
          <span className="text-[11px] text-editorial-muted">Cobertura nacional completa</span>
        </div>

        {/* KPI 2: Mayor Viabilidad (Destacada en Azul Marino/Índigo) */}
        <div className="bg-sidebar-bg text-white rounded-2xl p-5 border border-sidebar-border shadow-md flex flex-col justify-between">
          <span className="text-xs font-medium text-sidebar-muted">Mayor viabilidad</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black text-white">{kpis.top1_score || 0}</span>
            <span className="text-sm text-sidebar-muted font-medium">/100</span>
          </div>
          <span className="text-[11px] text-accent-sage font-medium truncate">
            {kpis.top1_nombre} lidera el índice
          </span>
        </div>

        {/* KPI 3: Energía Máximo */}
        <div className="bg-white rounded-2xl p-5 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <span className="text-xs font-medium text-editorial-muted">Energía · máximo</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black text-editorial-dark">{Math.round(kpis.max_energia_score || 0)}</span>
            <span className="text-sm text-editorial-muted font-medium">/100</span>
          </div>
          <span className="text-[11px] text-editorial-muted truncate">{kpis.max_energia_provincia}</span>
        </div>

        {/* KPI 4: Conectividad Máximo */}
        <div className="bg-white rounded-2xl p-5 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <span className="text-xs font-medium text-editorial-muted">Conectividad · máximo</span>
          <div className="my-2 flex items-baseline gap-1">
            <span className="text-3xl font-black text-editorial-dark">{Math.round(kpis.max_conectividad_score || 0)}</span>
            <span className="text-sm text-editorial-muted font-medium">/100</span>
          </div>
          <span className="text-[11px] text-editorial-muted truncate">{kpis.max_conectividad_provincia}</span>
        </div>

        {/* KPI 5: Dimensiones */}
        <div className="bg-white rounded-2xl p-5 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <span className="text-xs font-medium text-editorial-muted">Dimensiones del modelo</span>
          <div className="my-2">
            <span className="text-3xl font-black text-editorial-dark">6</span>
          </div>
          <span className="text-[11px] text-editorial-muted">MCDA con 6 macro-ejes</span>
        </div>
      </div>

      {/* Middle Section: Top 6 Bar Chart (2/3) + Lectura del Territorio (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 6 Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-base font-bold text-editorial-dark">
                Las provincias mejor posicionadas
              </h2>
              <span className="text-xs text-editorial-muted">Top 6 nacional</span>
            </div>
            <p className="text-xs text-editorial-muted mb-6">
              Índice compuesto de viabilidad · escala de 0 a 100
            </p>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={top6} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
                  <XAxis 
                    dataKey="nombre" 
                    tick={{ fill: '#7a7077', fontSize: 12, fontWeight: 500 }} 
                    axisLine={{ stroke: '#e4e1d7' }} 
                    tickLine={false} 
                  />
                  <YAxis 
                    domain={[0, 100]} 
                    ticks={[0, 25, 50, 75, 100]} 
                    tick={{ fill: '#a0999e', fontSize: 11 }} 
                    axisLine={{ stroke: '#e4e1d7' }} 
                    tickLine={false} 
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const item = payload[0].payload;
                        return (
                          <div className="bg-sidebar-bg text-white px-3 py-2 rounded-xl text-xs shadow-lg border border-sidebar-border">
                            <p className="font-bold">{item.nombreCompleto}</p>
                            <p className="text-sidebar-muted">Puntaje: <span className="font-bold text-white">{item.score}</span> /100</p>
                            <p className="text-sidebar-muted">Puesto #{item.rank} nacional</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                    {top6.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={index === 0 ? '#181829' : '#8fa8a2'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 border-t border-editorial-border/60 text-[11px] text-editorial-muted flex justify-between items-center">
            <span>Ponderación oficial: {perfilesConfig[activePerfil]?._nombre || activePerfil}</span>
            <button 
              onClick={() => onNavigate && onNavigate('matrix')}
              className="text-accent-indigo hover:underline font-semibold"
            >
              Ver las 24 provincias →
            </button>
          </div>
        </div>

        {/* Lectura del Territorio (Editorial Box) */}
        <div className="bg-accent-sageSoft/60 rounded-2xl p-6 border border-accent-sage/30 flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold tracking-widest text-accent-sageDark/80 uppercase mb-3">
              Lectura del territorio
            </div>
            <h3 className="text-2xl font-black text-editorial-dark tracking-tight leading-tight mb-4">
              {kpis.lectura_editorial?.titulo || 'La energía abre la oportunidad.'}
            </h3>
            <p className="text-sm text-editorial-dark/80 leading-relaxed mb-6 font-normal">
              {kpis.lectura_editorial?.cuerpo}
            </p>

            <div className="pt-4 border-t border-accent-sage/30">
              <h4 className="text-xs font-bold text-editorial-dark mb-1">
                El equilibrio importa
              </h4>
              <p className="text-xs text-editorial-dark/70 leading-relaxed">
                {kpis.lectura_editorial?.equilibrio}
              </p>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={() => onNavigate && onNavigate('simulator')}
              className="inline-flex items-center gap-2 text-sm font-bold text-accent-indigo hover:text-accent-indigoDark transition-colors group"
            >
              <span>Explorá las variables en el simulador</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Section: Un índice, seis perspectivas */}
      <div className="bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs">
        <div className="mb-4">
          <h2 className="text-base font-bold text-editorial-dark">
            Un índice, seis perspectivas
          </h2>
          <p className="text-xs text-editorial-muted">
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
                className="p-4 rounded-xl bg-canvas/60 border border-editorial-border/60 flex flex-col justify-between hover:bg-canvas transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold text-editorial-muted">
                      {dim.codigo}
                    </span>
                    <Icon className="w-4 h-4 text-accent-sageDark" />
                  </div>
                  <h3 className="text-sm font-bold text-editorial-dark mb-1">
                    {dim.nombre}
                  </h3>
                  <p className="text-xs text-editorial-muted line-clamp-3 leading-snug">
                    {dim.descripcion}
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-editorial-border/50 text-[11px] text-editorial-muted flex justify-between">
                  <span>Peso perfil:</span>
                  <strong className="text-editorial-dark">{weightPct}%</strong>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Disclaimer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-semibold tracking-wider uppercase text-editorial-muted/80">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Modelo auditado con fuentes públicas oficiales. Datos trazables a través de data_freshness.json.
        </span>
      </div>
    </div>
  );
}
