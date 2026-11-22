import React, { useState, useMemo, useEffect } from 'react';
import { useAppData } from '../../context/DataContext';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, useMap } from 'react-leaflet';
import { Zap, Layers, Check } from 'lucide-react';

// Colores vibrantes de alto contraste para fondo cartográfico oscuro (v2.1.0 — 6 Categorías)
const TEC_COLORS = {
  Hidroeléctrica: '#38BDF8', // Cian
  Eólica: '#34D399',         // Esmeralda claro
  Solar: '#FBBF24',          // Ámbar
  Térmica: '#F87171',        // Coral / Térmico
  Nuclear: '#A855F7',        // Púrpura eléctrico / Átomo
  Bioenergía: '#10B981',     // Verde biogénico
};

const ALL_TECS = ['Hidroeléctrica', 'Térmica', 'Solar', 'Eólica', 'Nuclear', 'Bioenergía'];

function MapRecenter({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom, { duration: 1.2 });
    }
  }, [center, zoom, map]);
  return null;
}

export default function View02Map() {
  const { data, activePerfil, selectedProvinceId, setSelectedProvinceId } = useAppData();

  // Multi-selección de tecnologías
  const [selectedTecs, setSelectedTecs] = useState(new Set(ALL_TECS));
  const [filterProvince, setFilterProvince] = useState(selectedProvinceId ? String(selectedProvinceId) : 'all');

  // Sincronizar selección
  useEffect(() => {
    if (filterProvince !== 'all') {
      setSelectedProvinceId(Number(filterProvince));
    }
  }, [filterProvince, setSelectedProvinceId]);

  if (!data) return null;

  const { jurisdicciones, centrales_sadi } = data;

  const activeProvince = useMemo(() => {
    return jurisdicciones.find((j) => j.id === Number(selectedProvinceId)) || jurisdicciones[0];
  }, [jurisdicciones, selectedProvinceId]);

  // Manejo de multi-selección
  const toggleTec = (tec) => {
    const next = new Set(selectedTecs);
    if (next.has(tec)) {
      if (next.size > 1) {
        next.delete(tec);
      }
    } else {
      next.add(tec);
    }
    setSelectedTecs(next);
  };

  const selectAllTecs = () => {
    setSelectedTecs(new Set(ALL_TECS));
  };

  const isAllSelected = selectedTecs.size === ALL_TECS.length;

  // Filtrado de centrales
  const filteredCentrales = useMemo(() => {
    return centrales_sadi.filter((c) => {
      const matchTec = selectedTecs.has(c.categoria_filtro);
      const matchProv = filterProvince === 'all' || c.jurisdiccion_id === Number(filterProvince);
      return matchTec && matchProv && c.lat && c.lon;
    });
  }, [centrales_sadi, selectedTecs, filterProvince]);

  // Centro y zoom dinámicos: CABA id 2 -> zoom 9, resto provincias -> zoom 6, general -> zoom 4
  const mapState = useMemo(() => {
    if (filterProvince !== 'all' && activeProvince?.lat && activeProvince?.lon) {
      const zoomLevel = activeProvince.id === 2 ? 9 : 6;
      return { center: [activeProvince.lat, activeProvince.lon], zoom: zoomLevel };
    }
    return { center: [-38.4161, -63.6167], zoom: 4 };
  }, [filterProvince, activeProvince]);

  const pData = activeProvince.scores_perfiles?.[activePerfil] || {};
  const scoreBase = Math.round(pData.score_base || 0);

  const nivelViabilidad = scoreBase >= 80 ? 'Viabilidad alta' : scoreBase >= 65 ? 'Viabilidad media' : 'Viabilidad inicial';

  const dimensionItems = [
    { key: 'subscore_energia', label: 'Energía', val: activeProvince.subscores?.subscore_energia || 0 },
    { key: 'subscore_conectividad', label: 'Conectividad', val: activeProvince.subscores?.subscore_conectividad || 0 },
    { key: 'subscore_clima', label: 'Clima', val: activeProvince.subscores?.subscore_clima || 0 },
    { key: 'subscore_fiscal', label: 'Fiscal / RIGI', val: activeProvince.subscores?.subscore_fiscal || 0 },
    { key: 'subscore_talento_riesgo', label: 'Talento / Riesgo', val: activeProvince.subscores?.subscore_talento_riesgo || 0 },
    { key: 'subscore_tier_readiness', label: 'Tier-Readiness', val: activeProvince.subscores?.subscore_tier_readiness || 0 },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="text-xs font-bold tracking-widest text-accent-cyan uppercase mb-1.5">
          Inteligencia Territorial / 02
        </div>
        <h1 className="text-3xl font-extrabold font-display text-editorial-dark tracking-tight">
          El territorio, en perspectiva
        </h1>
        <p className="text-sm font-medium text-editorial-muted mt-1 max-w-2xl">
          Explorá la distribución energética y el potencial de cada provincia sobre la cartografía oficial SADI.
        </p>
      </div>

      {/* Control Filter Bar */}
      <div className="bg-canvas-card rounded-2xl p-4 border border-editorial-border shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Multi-selección de Tecnologías Pills */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-bold text-editorial-muted mr-1">
            Centrales (multi-filtro):
          </span>
          <button
            onClick={selectAllTecs}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              isAllSelected
                ? 'bg-accent-cyan text-sidebar-bg shadow-xs'
                : 'bg-canvas text-editorial-muted border border-editorial-border hover:text-white'
            }`}
          >
            Todas
          </button>
          {ALL_TECS.map((tec) => {
            const isChecked = selectedTecs.has(tec);
            const color = TEC_COLORS[tec];
            return (
              <button
                key={tec}
                onClick={() => toggleTec(tec)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                  isChecked
                    ? 'bg-[#182235] text-white border-accent-cyan/50 shadow-2xs'
                    : 'bg-canvas text-editorial-muted/70 border-editorial-border hover:text-editorial-muted'
                }`}
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: color, opacity: isChecked ? 1 : 0.4 }}
                />
                <span>{tec}</span>
                {isChecked && <Check className="w-3 h-3 text-accent-cyan ml-0.5" />}
              </button>
            );
          })}
        </div>

        {/* Selector de Provincia */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-editorial-muted">
            Provincia:
          </span>
          <select
            value={filterProvince}
            onChange={(e) => {
              setFilterProvince(e.target.value);
              if (e.target.value !== 'all') {
                setSelectedProvinceId(Number(e.target.value));
              }
            }}
            className="px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas border border-editorial-border text-editorial-dark focus:outline-none focus:ring-1 focus:ring-accent-cyan"
          >
            <option value="all">Todas las provincias</option>
            {jurisdicciones.map((j) => (
              <option key={j.id} value={j.id}>
                {j.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Mapa GIS Nocturno (2/3) + Panel Provincia Destacada (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaflet Map Container */}
        <div className="lg:col-span-2 bg-canvas-card rounded-2xl p-4 border border-editorial-border shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-3 px-2">
            <div>
              <span className="text-[10px] font-bold tracking-widest uppercase text-accent-cyan">
                Argentina
              </span>
              <h2 className="text-sm font-bold text-editorial-dark">
                Infraestructura energética SADI ({filteredCentrales.length} centrales activas)
              </h2>
            </div>
            <span className="text-[11px] font-mono text-editorial-muted">
              Esri World Dark Gray · 0 API Keys
            </span>
          </div>

          {/* Map Viewport con Esri Dark Gray */}
          <div className="w-full h-[520px] rounded-xl overflow-hidden relative border border-editorial-border bg-[#080A12]">
            <MapContainer
              center={mapState.center}
              zoom={mapState.zoom}
              scrollWheelZoom={false}
              className="w-full h-full"
            >
              <MapRecenter center={mapState.center} zoom={mapState.zoom} />
              
              {/* Esri World Dark Gray Base: fondo nocturno oficial sin API key */}
              <TileLayer
                attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
              />

              {/* CircleMarkers vectoriales de alto contraste */}
              {filteredCentrales.map((c) => {
                const color = TEC_COLORS[c.categoria_filtro] || '#38BDF8';
                const radius = Math.min(Math.max(Math.sqrt(c.potencia_mw || 10) * 0.45, 3.5), 10);

                return (
                  <CircleMarker
                    key={c.id}
                    center={[c.lat, c.lon]}
                    radius={radius}
                    pathOptions={{
                      color: '#080A12',
                      weight: 1.5,
                      fillColor: color,
                      fillOpacity: 0.9,
                    }}
                  >
                    <Tooltip direction="top" offset={[0, -5]} opacity={0.96}>
                      <div className="text-xs bg-sidebar-bg text-white p-1 rounded">
                        <strong className="block font-bold text-accent-cyan">{c.nombre}</strong>
                        <span className="text-editorial-body">{c.categoria_filtro} · <strong className="tabular-nums text-white">{c.potencia_mw} MW</strong></span>
                        <div className="text-[10px] text-editorial-muted">{c.jurisdiccion_nombre}</div>
                      </div>
                    </Tooltip>
                    <Popup>
                      <div className="p-1 text-xs">
                        <h4 className="font-bold text-sm text-editorial-dark mb-1">{c.nombre}</h4>
                        <p><strong>Tecnología:</strong> {c.tecnologia_original}</p>
                        <p><strong>Potencia instalada:</strong> <span className="tabular-nums font-bold">{c.potencia_mw} MW</span></p>
                        <p><strong>Provincia:</strong> {c.jurisdiccion_nombre}</p>
                        <button
                          onClick={() => {
                            setSelectedProvinceId(c.jurisdiccion_id);
                            setFilterProvince(String(c.jurisdiccion_id));
                          }}
                          className="mt-2 text-accent-cyan hover:underline font-semibold block"
                        >
                          Ver perfil de {c.jurisdiccion_nombre} →
                        </button>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>

          {/* Bottom Map Legend */}
          <div className="mt-3 px-3.5 py-2.5 bg-canvas rounded-xl flex items-center justify-between flex-wrap gap-3 text-xs text-editorial-subtitle border border-editorial-border font-medium">
            <div className="flex items-center gap-3.5 flex-wrap">
              {ALL_TECS.map((tec) => (
                <div key={tec} className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TEC_COLORS[tec] }} />
                  <span>{tec}</span>
                </div>
              ))}
            </div>
            <span className="text-[11px] text-editorial-muted font-mono">
              Radio escalado por potencia (MW)
            </span>
          </div>
        </div>

        {/* Right Panel: Provincia Destacada */}
        <div className="bg-canvas-card rounded-2xl p-6 border border-editorial-border shadow-xs flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold tracking-widest uppercase text-accent-cyan mb-1">
              Provincia destacada
            </div>
            <h2 className="text-2xl font-black font-display text-white tracking-tight">
              {activeProvince.nombre}
            </h2>
            <p className="text-xs text-editorial-muted mb-5 font-medium">
              {activeProvince.region} · Arquetipo: <span className="font-bold text-accent-cyan">{activeProvince.cluster?.nombre}</span>
            </p>

            {/* Score box */}
            <div className="bg-[#10192A] rounded-2xl p-5 border border-accent-cyan/30 mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-black font-display text-white tabular-nums">{scoreBase}</span>
                <span className="text-sm font-bold text-accent-cyan">/100</span>
              </div>
              <p className="text-xs font-bold text-accent-emerald mt-1">
                {nivelViabilidad}
              </p>
              <p className="text-[11px] text-editorial-body mt-2 leading-relaxed font-normal">
                {activeProvince.cluster?.descripcion}
              </p>
            </div>

            {/* Perfil Provincial: 6 Dimensiones con Barras */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-editorial-muted mb-3.5">
                Perfil provincial (6 dimensiones)
              </h3>
              <div className="space-y-3">
                {dimensionItems.map((item) => {
                  const valRound = Math.round(item.val);
                  return (
                    <div key={item.key}>
                      <div className="flex justify-between items-center text-xs mb-1">
                        <span className="font-semibold text-editorial-subtitle">{item.label}</span>
                        <span className="font-bold text-white tabular-nums font-mono">{valRound}</span>
                      </div>
                      <div className="w-full bg-canvas rounded-full h-1.5 overflow-hidden border border-editorial-border/40">
                        <div
                          className="bg-accent-cyan h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(valRound, 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-editorial-border text-[11px] text-editorial-muted leading-relaxed">
            Puntajes derivados de la tabla maestra auditada. Cero valores sintéticos.
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-bold tracking-wider uppercase text-editorial-muted">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Base geográfica: Secretaría de Energía / CAMMESA · 474 centrales SADI georreferenciadas.
        </span>
      </div>
    </div>
  );
}
