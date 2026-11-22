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
  Legend
} from 'recharts';
import { RotateCcw, Sliders, ArrowUp, ArrowDown, Minus, Filter, AlertTriangle } from 'lucide-react';

const DIMENSIONS_CONFIG = [
  { 
    id: 'subscore_energia', 
    label: 'Energía', 
    shortLabel: 'Energía',
    desc: 'Potencia SADI instalada en MW y porcentaje de generación renovable.'
  },
  { 
    id: 'subscore_conectividad', 
    label: 'Conectividad', 
    shortLabel: 'Conectividad',
    desc: 'Latencia a Las Toninas, capilaridad FTTH y densidad de fibra troncal.'
  },
  { 
    id: 'subscore_clima', 
    label: 'Clima y PUE', 
    shortLabel: 'Clima',
    desc: 'Horas de free cooling anual, eficiencia térmica y bajo PUE.'
  },
  { 
    id: 'subscore_fiscal', 
    label: 'Fiscal / RIGI', 
    shortLabel: 'Fiscal',
    desc: 'Adhesión provincial a Ley 27.742 e incentivos en IIBB tecnológico.'
  },
  { 
    id: 'subscore_talento_riesgo', 
    label: 'Talento / Riesgo', 
    shortLabel: 'Talento',
    desc: 'Puestos privados de software/TIC y bajo riesgo sísmico (INPRES).'
  },
  { 
    id: 'subscore_tier_readiness', 
    label: 'Tier-Readiness', 
    shortLabel: 'Tier',
    desc: 'Resiliencia de sitio, doble acometida y aptitud geotécnica/hídrica.'
  },
];

function getPriorityLabel(val) {
  if (val === 0) return { label: 'Ignorar', color: 'text-editorial-muted' };
  if (val <= 3) return { label: 'Baja', color: 'text-slate-400' };
  if (val <= 6) return { label: 'Media', color: 'text-accent-cyan' };
  if (val <= 8) return { label: 'Alta', color: 'text-accent-amber' };
  return { label: 'Crítica', color: 'text-emerald-400' };
}

export default function View03Simulator() {
  const { data, selectedProvinceId, setSelectedProvinceId } = useAppData();

  // Escala 0 a 10 de prioridad por dimensión
  const [priorities, setPriorities] = useState({
    subscore_energia: 5,
    subscore_conectividad: 5,
    subscore_clima: 5,
    subscore_fiscal: 5,
    subscore_talento_riesgo: 5,
    subscore_tier_readiness: 5,
  });

  const [activeTemplate, setActiveTemplate] = useState('personalizado');

  // Requisitos mínimos técnicos opcionales
  const [minSadiMw, setMinSadiMw] = useState(0); // 0, 200, 500, 1000
  const [onlyRigi, setOnlyRigi] = useState(false); // boolean
  const [minClimaSubscore, setMinClimaSubscore] = useState(0); // 0, 60, 75

  const [selectedProvId, setSelectedProvId] = useState(
    selectedProvinceId ? Number(selectedProvinceId) : 58
  );

  if (!data) return null;

  const { jurisdicciones, centrales_sadi } = data;

  // Potencia SADI total acumulada por provincia (en MW)
  const sadiMwPorProvincia = useMemo(() => {
    const map = {};
    centrales_sadi.forEach((c) => {
      const jid = c.jurisdiccion_id;
      map[jid] = (map[jid] || 0) + (c.potencia_mw || 0);
    });
    return map;
  }, [centrales_sadi]);

  // Promedio nacional por dimensión para el Radar
  const promediosNacionales = useMemo(() => {
    const sums = {};
    DIMENSIONS_CONFIG.forEach((d) => (sums[d.id] = 0));
    jurisdicciones.forEach((j) => {
      DIMENSIONS_CONFIG.forEach((d) => {
        sums[d.id] += j.subscores?.[d.id] || 0;
      });
    });
    const avg = {};
    DIMENSIONS_CONFIG.forEach((d) => {
      avg[d.id] = Math.round((sums[d.id] / jurisdicciones.length) * 10) / 10;
    });
    return avg;
  }, [jurisdicciones]);

  // Ranking equilibrado base para calcular deltas de cambio de puesto (▲/▼/=)
  const rankingBaseEquilibrado = useMemo(() => {
    const list = jurisdicciones.map((j) => {
      let scoreEq = 0;
      DIMENSIONS_CONFIG.forEach((d) => {
        scoreEq += (j.subscores?.[d.id] || 0) / 6;
      });
      return { id: j.id, scoreEq };
    });
    list.sort((a, b) => b.scoreEq - a.scoreEq);
    const ranks = {};
    list.forEach((item, idx) => {
      ranks[item.id] = idx + 1;
    });
    return ranks;
  }, [jurisdicciones]);

  // Plantillas de partida rápidas
  const applyTemplate = (templateKey) => {
    setActiveTemplate(templateKey);
    if (templateKey === 'campus_ia') {
      setPriorities({
        subscore_energia: 10,
        subscore_clima: 8,
        subscore_tier_readiness: 6,
        subscore_fiscal: 6,
        subscore_conectividad: 4,
        subscore_talento_riesgo: 4,
      });
    } else if (templateKey === 'nodo_edge') {
      setPriorities({
        subscore_conectividad: 10,
        subscore_talento_riesgo: 8,
        subscore_tier_readiness: 6,
        subscore_energia: 5,
        subscore_fiscal: 4,
        subscore_clima: 3,
      });
    } else if (templateKey === 'equilibrado' || templateKey === 'reset') {
      setPriorities({
        subscore_energia: 5,
        subscore_conectividad: 5,
        subscore_clima: 5,
        subscore_fiscal: 5,
        subscore_talento_riesgo: 5,
        subscore_tier_readiness: 5,
      });
    }
  };

  const handleSliderChange = (dimId, newVal) => {
    setActiveTemplate('personalizado');
    const val = Math.max(0, Math.min(10, Number(newVal)));
    setPriorities((prev) => ({
      ...prev,
      [dimId]: val,
    }));
  };

  // Suma total y pesos efectivos normalizados
  const sumPriorities = useMemo(() => {
    return Object.values(priorities).reduce((a, b) => a + b, 0);
  }, [priorities]);

  const effectiveWeights = useMemo(() => {
    const eff = {};
    if (sumPriorities === 0) {
      DIMENSIONS_CONFIG.forEach((d) => (eff[d.id] = 100 / DIMENSIONS_CONFIG.length));
    } else {
      DIMENSIONS_CONFIG.forEach((d) => {
        eff[d.id] = ((priorities[d.id] || 0) / sumPriorities) * 100;
      });
    }
    return eff;
  }, [priorities, sumPriorities]);

  // Recalcular scores y evaluar cumplimiento de requisitos técnicos
  const rankingSimulado = useMemo(() => {
    return jurisdicciones
      .map((j) => {
        let score = 0;
        DIMENSIONS_CONFIG.forEach((dim) => {
          const wEff = effectiveWeights[dim.id] / 100;
          const sub = j.subscores?.[dim.id] || 0;
          score += sub * wEff;
        });
        const scoreRound = Math.round(score * 10) / 10;
        const rankBase = rankingBaseEquilibrado[j.id] || 12;

        // Evaluación de Requisitos Técnicos Mínimos
        const sadiMw = sadiMwPorProvincia[j.id] || 0;
        const cumpleMw = sadiMw >= minSadiMw;
        const cumpleRigi = !onlyRigi || (j.subscores?.subscore_fiscal || 0) >= 80;
        const cumpleClima = (j.subscores?.subscore_clima || 0) >= minClimaSubscore;
        const cumpleRequisitos = cumpleMw && cumpleRigi && cumpleClima;

        let motivoExclusion = null;
        if (!cumpleMw) motivoExclusion = `< ${minSadiMw} MW SADI`;
        else if (!cumpleRigi) motivoExclusion = 'Sin adhesión formal RIGI';
        else if (!cumpleClima) motivoExclusion = 'Eficiencia térmica insuficiente';

        return {
          id: j.id,
          nombre: j.nombre,
          corta: j.corta || j.nombre,
          region: j.region,
          score: scoreRound,
          cluster: j.cluster?.nombre,
          subscores: j.subscores,
          rankBase,
          sadiMw: Math.round(sadiMw),
          cumpleRequisitos,
          motivoExclusion
        };
      })
      .sort((a, b) => {
        // Ordenar primero las que cumplen requisitos por score descendente
        if (a.cumpleRequisitos && !b.cumpleRequisitos) return -1;
        if (!a.cumpleRequisitos && b.cumpleRequisitos) return 1;
        return b.score - a.score;
      })
      .map((j, idx) => {
        const rankSim = idx + 1;
        const deltaRank = j.rankBase - rankSim;
        return { ...j, rank: rankSim, deltaRank };
      });
  }, [jurisdicciones, effectiveWeights, rankingBaseEquilibrado, sadiMwPorProvincia, minSadiMw, onlyRigi, minClimaSubscore]);

  // Provincia actualmente activa
  const activeProvince = useMemo(() => {
    return (
      rankingSimulado.find((j) => j.id === selectedProvId) || rankingSimulado[0]
    );
  }, [rankingSimulado, selectedProvId]);

  const scorePromedioNacional = useMemo(() => {
    const total = rankingSimulado.reduce((acc, curr) => acc + curr.score, 0);
    return Math.round((total / rankingSimulado.length) * 10) / 10;
  }, [rankingSimulado]);

  const radarData = useMemo(() => {
    if (!activeProvince) return [];
    return DIMENSIONS_CONFIG.map((dim) => ({
      dimension: dim.shortLabel,
      Provincia: Math.round(activeProvince.subscores?.[dim.id] || 0),
      PromedioNacional: promediosNacionales[dim.id] || 50,
      fullMark: 100,
    }));
  }, [activeProvince, promediosNacionales]);

  const desgloseContribucion = useMemo(() => {
    if (!activeProvince) return [];
    return DIMENSIONS_CONFIG.map((dim) => {
      const sub = activeProvince.subscores?.[dim.id] || 0;
      const wEff = effectiveWeights[dim.id] || 0;
      const contrib = (sub * (wEff / 100));
      return {
        id: dim.id,
        label: dim.label,
        subscore: Math.round(sub),
        effectiveWeight: wEff.toFixed(1),
        puntosContribucion: contrib.toFixed(1),
      };
    });
  }, [activeProvince, effectiveWeights]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-xs font-bold tracking-widest text-accent-cyan uppercase mb-1.5">
            Inteligencia Territorial / 03
          </div>
          <h1 className="text-3xl font-extrabold font-display text-editorial-dark tracking-tight">
            Diseñá tu escenario ideal
          </h1>
          <p className="text-sm font-medium text-editorial-muted mt-1 max-w-2xl">
            Ajustá las prioridades del 0 al 10 y definí filtros técnicos mínimos para ordenar el territorio.
          </p>
        </div>

        {/* Badge modo activo */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-editorial-muted">Configuración:</span>
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#131E33] text-accent-cyan border border-accent-cyan/40 shadow-xs">
            {activeTemplate === 'personalizado' ? 'Perfil libre' : `Plantilla: ${activeTemplate}`}
          </span>
        </div>
      </div>

      {/* Barra de Requisitos Mínimos Técnicos (Opcionales) */}
      <div className="bg-canvas-card rounded-2xl p-4 border border-editorial-border shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-accent-cyan" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Requisitos Técnicos Mínimos:
          </span>
        </div>

        <div className="flex items-center gap-6 flex-wrap text-xs">
          {/* Potencia SADI */}
          <div className="flex items-center gap-2">
            <span className="text-editorial-muted font-medium">Potencia SADI mínima:</span>
            <select
              value={minSadiMw}
              onChange={(e) => setMinSadiMw(Number(e.target.value))}
              className="px-2.5 py-1 rounded-lg bg-canvas border border-editorial-border text-white text-xs font-bold focus:outline-none"
            >
              <option value={0}>Sin umbral</option>
              <option value={200}>≥ 200 MW</option>
              <option value={500}>≥ 500 MW</option>
              <option value={1000}>≥ 1.000 MW</option>
            </select>
          </div>

          {/* Clima / Eficiencia Térmica */}
          <div className="flex items-center gap-2">
            <span className="text-editorial-muted font-medium">Clima (Free Cooling):</span>
            <select
              value={minClimaSubscore}
              onChange={(e) => setMinClimaSubscore(Number(e.target.value))}
              className="px-2.5 py-1 rounded-lg bg-canvas border border-editorial-border text-white text-xs font-bold focus:outline-none"
            >
              <option value={0}>Sin umbral</option>
              <option value={60}>Moderado (Score ≥ 60)</option>
              <option value={75}>Alta eficiencia (Score ≥ 75)</option>
            </select>
          </div>

          {/* RIGI Toggle */}
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={onlyRigi}
              onChange={(e) => setOnlyRigi(e.target.checked)}
              className="w-4 h-4 rounded bg-canvas border-editorial-border accent-accent-cyan cursor-pointer"
            />
            <span className={`font-semibold ${onlyRigi ? 'text-accent-emerald font-bold' : 'text-editorial-muted'}`}>
              Solo provincias adheridas al RIGI
            </span>
          </label>
        </div>
      </div>

      {/* BLOQUE 1 (ARRIBA): Parametrización (2 cols) vs Ranking en Tiempo Real (3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        
        {/* Columna Izquierda: Parametrización 0-10 (2 cols) */}
        <div className="lg:col-span-2 bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-accent-cyan" />
                <h2 className="text-base font-bold font-display text-white">
                  Nivel de Prioridad (0 a 10)
                </h2>
              </div>
              <button
                onClick={() => applyTemplate('reset')}
                title="Restablecer valores neutros"
                className="flex items-center gap-1 text-xs font-semibold text-editorial-muted hover:text-white transition-colors px-2 py-1 rounded-lg hover:bg-canvas"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Restablecer</span>
              </button>
            </div>
            
            <p className="text-xs text-editorial-muted mb-4 font-normal leading-relaxed">
              Definí el peso relativo de cada macro-eje. Las ponderaciones porcentuales se recalculan de forma proporcional.
            </p>

            {/* Plantillas de partida rápidas */}
            <div className="mb-5 pb-4 border-b border-editorial-border">
              <span className="text-[10px] font-bold tracking-wider uppercase text-editorial-muted block mb-2">
                Plantillas de partida
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => applyTemplate('campus_ia')}
                  className={`px-2 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                    activeTemplate === 'campus_ia'
                      ? 'bg-accent-cyan text-sidebar-bg border-accent-cyan'
                      : 'bg-canvas hover:bg-canvas-muted text-editorial-subtitle border-editorial-border'
                  }`}
                >
                  Campus IA
                </button>
                <button
                  onClick={() => applyTemplate('nodo_edge')}
                  className={`px-2 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                    activeTemplate === 'nodo_edge'
                      ? 'bg-accent-cyan text-sidebar-bg border-accent-cyan'
                      : 'bg-canvas hover:bg-canvas-muted text-editorial-subtitle border-editorial-border'
                  }`}
                >
                  Nodos Edge
                </button>
                <button
                  onClick={() => applyTemplate('equilibrado')}
                  className={`px-2 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                    activeTemplate === 'equilibrado'
                      ? 'bg-accent-cyan text-sidebar-bg border-accent-cyan'
                      : 'bg-canvas hover:bg-canvas-muted text-editorial-subtitle border-editorial-border'
                  }`}
                >
                  Equilibrado
                </button>
              </div>
            </div>

            {/* 6 Sliders con escala 0-10 y micro-descripción */}
            <div className="space-y-4">
              {DIMENSIONS_CONFIG.map((dim) => {
                const priorityVal = priorities[dim.id] || 0;
                const effVal = effectiveWeights[dim.id] || 0;
                const priorityInfo = getPriorityLabel(priorityVal);

                return (
                  <div key={dim.id} className="group">
                    <div className="flex justify-between items-center text-xs mb-0.5">
                      <span className="font-bold text-white">
                        {dim.label}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className={`text-[11px] font-bold ${priorityInfo.color}`}>
                          {priorityVal} · {priorityInfo.label}
                        </span>
                        <span className="text-[11px] font-mono font-bold text-accent-cyan tabular-nums min-w-[42px] text-right">
                          {effVal.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    
                    <input
                      type="range"
                      min="0"
                      max="10"
                      step="1"
                      value={priorityVal}
                      onChange={(e) => handleSliderChange(dim.id, e.target.value)}
                      className="w-full accent-accent-cyan cursor-pointer h-1.5 bg-canvas rounded-lg"
                    />

                    <p className="text-[10px] text-editorial-muted leading-tight mt-0.5 font-normal">
                      {dim.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-5 pt-3.5 border-t border-editorial-border flex items-center justify-between text-xs text-editorial-muted">
            <span>Intensidad total: <strong className="text-white tabular-nums">{sumPriorities} / 60 pts</strong></span>
            <span className="text-accent-cyan font-bold font-mono">100.0% Ponderado</span>
          </div>
        </div>

        {/* Columna Derecha: Ranking Territorial en Tiempo Real (3 cols) */}
        <div className="lg:col-span-3 bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <div>
                <h2 className="text-base font-bold font-display text-white">
                  Ranking Dinámico en Tiempo Real
                </h2>
                <p className="text-xs text-editorial-muted">
                  Impacto provincial instantáneo con aplicación de umbrales técnicos.
                </p>
              </div>
              <span className="text-xs font-semibold text-accent-cyan bg-canvas px-2.5 py-1 rounded-full border border-editorial-border">
                24 jurisdicciones
              </span>
            </div>

            {/* Encabezado de tabla */}
            <div className="mt-3 grid grid-cols-12 text-[10px] font-bold tracking-wider uppercase text-editorial-muted pb-2 border-b border-editorial-border px-2">
              <span className="col-span-2">Puesto</span>
              <span className="col-span-5">Provincia</span>
              <span className="col-span-3">Puntaje</span>
              <span className="col-span-2 text-right">vs. Base</span>
            </div>

            {/* Lista scrolleable con las 24 provincias */}
            <div className="overflow-y-auto max-h-[420px] divide-y divide-editorial-border/40 pr-1">
              {rankingSimulado.map((prov) => {
                const isSelected = prov.id === selectedProvId;
                const delta = prov.deltaRank;
                const isCompliant = prov.cumpleRequisitos;

                return (
                  <div
                    key={prov.id}
                    onClick={() => {
                      setSelectedProvId(prov.id);
                      setSelectedProvinceId(prov.id);
                    }}
                    className={`grid grid-cols-12 items-center py-2 px-2.5 rounded-xl cursor-pointer text-xs transition-colors ${
                      isSelected
                        ? 'bg-[#182338] font-semibold border border-accent-cyan/60 shadow-xs'
                        : isCompliant
                        ? 'hover:bg-canvas/60'
                        : 'opacity-50 hover:opacity-80 bg-rose-950/10'
                    }`}
                  >
                    {/* Puesto */}
                    <div className="col-span-2 flex items-center gap-1 font-mono">
                      <span className={`font-bold tabular-nums ${isCompliant ? 'text-white' : 'text-rose-400'}`}>
                        #{String(prov.rank).padStart(2, '0')}
                      </span>
                    </div>

                    {/* Nombre y Región */}
                    <div className="col-span-5 truncate pr-2">
                      <div className="flex items-center gap-1.5 truncate">
                        <span className={`font-bold truncate ${isCompliant ? 'text-white' : 'text-slate-400'}`}>
                          {prov.nombre}
                        </span>
                        {!isCompliant && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-rose-950 text-rose-300 border border-rose-800 shrink-0">
                            Excluida
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-editorial-muted font-normal block truncate">
                        {isCompliant ? `${prov.region} · ${prov.sadiMw} MW SADI` : prov.motivoExclusion}
                      </span>
                    </div>

                    {/* Barra de progreso y puntaje */}
                    <div className="col-span-3 pr-2">
                      <div className="flex items-center justify-between text-[11px] mb-0.5">
                        <span className="font-black text-white tabular-nums font-display">
                          {prov.score}
                        </span>
                      </div>
                      <div className="w-full bg-canvas rounded-full h-1.5 overflow-hidden">
                        <div
                          className="h-1.5 rounded-full transition-all duration-300"
                          style={{
                            width: `${Math.min(prov.score, 100)}%`,
                            backgroundColor: isCompliant
                              ? isSelected ? '#38BDF8' : '#2563EB'
                              : '#64748B',
                          }}
                        />
                      </div>
                    </div>

                    {/* Delta de cambio de puesto */}
                    <div className="col-span-2 text-right">
                      {isCompliant ? (
                        delta > 0 ? (
                          <span className="inline-flex items-center gap-0.5 text-[11px] font-bold text-accent-emerald bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800">
                            <ArrowUp className="w-3 h-3" />
                            <span className="tabular-nums">+{delta}</span>
                          </span>
                        ) : delta < 0 ? (
                          <span className="inline-flex items-center gap-0.5 text-[11px] font-bold text-rose-400 bg-rose-950/40 px-1.5 py-0.5 rounded border border-rose-800">
                            <ArrowDown className="w-3 h-3" />
                            <span className="tabular-nums">{delta}</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-0.5 text-[11px] font-medium text-editorial-muted bg-canvas px-1.5 py-0.5 rounded border border-editorial-border">
                            <Minus className="w-3 h-3" />
                            <span className="tabular-nums">0</span>
                          </span>
                        )
                      ) : (
                        <span className="text-[10px] text-rose-400 font-mono">Filtro</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-3 border-t border-editorial-border text-[11px] text-editorial-muted flex items-center justify-between">
            <span>Promedio nacional: <strong className="text-white tabular-nums">{scorePromedioNacional} pts</strong></span>
            <span>Provincia en foco: <strong className="text-accent-cyan">{activeProvince.nombre}</strong></span>
          </div>
        </div>
      </div>

      {/* BLOQUE 2 (ABAJO): Espectro de Viabilidad Ancho Completo */}
      <div className="bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-4 border-b border-editorial-border">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold tracking-widest uppercase text-accent-cyan">
                Espectro de Viabilidad Multidimensional
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan" />
              <span className="text-xs font-bold text-white">
                {activeProvince.nombre}
              </span>
            </div>
            <h2 className="text-xl font-black font-display text-white tracking-tight mt-0.5">
              Comparativa Territorial frente al Promedio Nacional
            </h2>
          </div>

          {/* Selector de provincia */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-editorial-muted">Inspeccionar:</span>
            <select
              value={selectedProvId}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedProvId(id);
                setSelectedProvinceId(id);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas border border-editorial-border text-white focus:outline-none focus:ring-1 focus:ring-accent-cyan"
            >
              {jurisdicciones.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Grid de 3 columnas del Espectro */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          
          {/* Radar Hexagonal Recharts (5 cols) */}
          <div className="lg:col-span-5 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="#232B3E" strokeDasharray="3 3" />
                <PolarAngleAxis
                  dataKey="dimension"
                  tick={{ fill: '#CBD5E1', fontSize: 11, fontWeight: 600 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  ticks={[25, 50, 75, 100]}
                  tick={{ fill: '#64748B', fontSize: 9 }}
                  axisLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="bg-sidebar-bg text-white px-3 py-2 rounded-xl text-xs shadow-xl border border-editorial-border space-y-1">
                          <p className="font-bold text-accent-cyan">{item.dimension}</p>
                          <p className="flex justify-between gap-4">
                            <span className="text-editorial-muted">{activeProvince.nombre}:</span>
                            <span className="font-bold tabular-nums text-white">{item.Provincia} pts</span>
                          </p>
                          <p className="flex justify-between gap-4 text-editorial-muted">
                            <span>Promedio Nacional:</span>
                            <span className="font-bold tabular-nums">{item.PromedioNacional} pts</span>
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend 
                  wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} 
                  iconType="circle"
                />
                <Radar
                  name="Promedio Nacional"
                  dataKey="PromedioNacional"
                  stroke="#64748B"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  fill="none"
                />
                <Radar
                  name={activeProvince.nombre}
                  dataKey="Provincia"
                  stroke="#38BDF8"
                  strokeWidth={2}
                  fill="#38BDF8"
                  fillOpacity={0.35}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Tarjeta de Puntaje y Posición Destacada (3 cols) */}
          <div className="lg:col-span-3 bg-[#10192A] rounded-2xl p-6 border border-accent-cyan/30 flex flex-col justify-between h-72">
            <div>
              <span className="text-[10px] font-bold tracking-widest uppercase text-accent-cyan block mb-1">
                Puntaje en este escenario
              </span>
              <div className="flex items-baseline gap-1 my-1">
                <span className="text-4xl font-black font-display text-white tabular-nums">
                  {activeProvince.score}
                </span>
                <span className="text-xs font-bold text-accent-cyan">/100</span>
              </div>

              <div className="mt-4 pt-3 border-t border-editorial-border space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-editorial-body font-medium">Posición nacional:</span>
                  <span className="font-bold text-white tabular-nums font-mono">
                    #{String(activeProvince.rank).padStart(2, '0')} de 24
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-editorial-body font-medium">Delta vs. Promedio:</span>
                  <span className={`font-bold tabular-nums ${activeProvince.score >= scorePromedioNacional ? 'text-accent-emerald' : 'text-rose-400'}`}>
                    {activeProvince.score >= scorePromedioNacional ? '+' : ''}{(activeProvince.score - scorePromedioNacional).toFixed(1)} pts
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-editorial-body font-medium">Potencia SADI:</span>
                  <span className="font-bold text-accent-amber tabular-nums">
                    {activeProvince.sadiMw} MW
                  </span>
                </div>
              </div>
            </div>

            <div>
              <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border shadow-2xs block text-center ${
                activeProvince.cumpleRequisitos
                  ? 'bg-emerald-950/40 text-accent-emerald border-emerald-800'
                  : 'bg-rose-950/40 text-rose-300 border-rose-800'
              }`}>
                {activeProvince.cumpleRequisitos ? 'Cumple requisitos técnicos' : activeProvince.motivoExclusion}
              </span>
            </div>
          </div>

          {/* Desglose de Contribución por Dimensión (4 cols) */}
          <div className="lg:col-span-4 bg-canvas rounded-2xl p-5 border border-editorial-border h-72 flex flex-col justify-between">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-editorial-subtitle mb-2">
                Desglose de Aportes al Puntaje
              </h3>
              <p className="text-[11px] text-editorial-muted mb-3">
                Subscore provincial × Peso relativo configurado = Puntos aportados
              </p>

              <div className="space-y-2">
                {desgloseContribucion.map((item) => (
                  <div key={item.id} className="flex items-center justify-between text-xs">
                    <span className="font-medium text-white truncate max-w-[140px]">
                      {item.label}
                    </span>
                    <div className="flex items-center gap-2 font-mono text-[11px]">
                      <span className="text-editorial-muted tabular-nums">
                        {item.subscore} × {item.effectiveWeight}%
                      </span>
                      <span className="text-editorial-border">=</span>
                      <span className="font-bold text-accent-cyan tabular-nums min-w-[34px] text-right">
                        {item.puntosContribucion}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-editorial-border text-[11px] text-editorial-muted flex justify-between font-medium">
              <span>Suma de aportes:</span>
              <strong className="text-white tabular-nums font-mono">{activeProvince.score} pts</strong>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
