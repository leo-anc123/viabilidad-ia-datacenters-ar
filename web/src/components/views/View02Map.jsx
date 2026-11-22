import React, { useState, useMemo, useEffect } from 'react';
import { useAppData } from '../../context/DataContext';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, useMap } from 'react-leaflet';
import { Zap, Layers } from 'lucide-react';

// Colores editoriales por categoría tecnológica
const TEC_COLORS = {
  Hidroeléctrica: '#4c2e43', // Ciruela oscuro
  Eólica: '#4d8a78',         // Salvia vibrante
  Solar: '#d4882c',          // Ámbar/dorado editorial
  Térmica: '#3d445c',        // Pizarra índigo
};

// Componente para reencuadrar el mapa cuando cambia la provincia seleccionada
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

  const [selectedTec, setSelectedTec] = useState('Todas');
  const [filterProvince, setFilterProvince] = useState(selectedProvinceId ? String(selectedProvinceId) : 'all');

  // Sincronizar selección
  useEffect(() => {
    if (filterProvince !== 'all') {
      setSelectedProvinceId(Number(filterProvince));
    }
  }, [filterProvince, setSelectedProvinceId]);

  if (!data) return null;

  const { jurisdicciones, centrales_sadi } = data;

  // Provincia actualmente activa para el panel lateral
  const activeProvince = useMemo(() => {
    return jurisdicciones.find((j) => j.id === Number(selectedProvinceId)) || jurisdicciones[0];
  }, [jurisdicciones, selectedProvinceId]);

  // Filtrado de centrales
  const filteredCentrales = useMemo(() => {
    return centrales_sadi.filter((c) => {
      const matchTec = selectedTec === 'Todas' || c.categoria_filtro === selectedTec;
      const matchProv = filterProvince === 'all' || c.jurisdiccion_id === Number(filterProvince);
      return matchTec && matchProv && c.lat && c.lon;
    });
  }, [centrales_sadi, selectedTec, filterProvince]);

  // Centro y zoom dinámicos
  const mapState = useMemo(() => {
    if (filterProvince !== 'all' && activeProvince?.lat && activeProvince?.lon) {
      return { center: [activeProvince.lat, activeProvince.lon], zoom: 6 };
    }
    return { center: [-38.4161, -63.6167], zoom: 4 }; // Centro Argentina
  }, [filterProvince, activeProvince]);

  const pData = activeProvince.scores_perfiles?.[activePerfil] || {};
  const scoreBase = Math.round(pData.score_base || 0);

  // Nivel semántico
  const nivelViabilidad = scoreBase >= 80 ? 'Viabilidad alta' : scoreBase >= 65 ? 'Viabilidad media' : 'Viabilidad inicial';

  // Dimensiones para la barra de perfil provincial
  const dimensionItems = [
    { key: 'subscore_energia', label: 'Energía', val: activeProvince.subscores?.subscore_energia || 0 },
    { key: 'subscore_conectividad', label: 'Conectividad', val: activeProvince.subscores?.subscore_conectividad || 0 },
    { key: 'subscore_clima', label: 'Clima', val: activeProvince.subscores?.subscore_clima || 0 },
    { key: 'subscore_fiscal', label: 'Fiscal / RIGI', val: activeProvince.subscores?.subscore_fiscal || 0 },
    { key: 'subscore_talento_riesgo', label: 'Talento / Riesgo', val: activeProvince.subscores?.subscore_talento_riesgo || 0 },
    { key: 'subscore_tier_readiness', label: 'Tier-Readiness', val: activeProvince.subscores?.subscore_tier_readiness || 0 },
  ];

  const tecFilters = ['Todas', 'Hidroeléctrica', 'Eólica', 'Solar', 'Térmica'];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="text-xs font-bold tracking-widest text-accent-indigo uppercase mb-1.5">
          Inteligencia Territorial / 02
        </div>
        <h1 className="text-3xl font-extrabold text-editorial-dark tracking-tight">
          El territorio, en perspectiva
        </h1>
        <p className="text-sm text-editorial-muted mt-1 max-w-2xl">
          Explorá la distribución energética y el potencial de cada provincia.
        </p>
      </div>

      {/* Control Filter Bar */}
      <div className="bg-white rounded-2xl p-4 border border-editorial-border/80 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Tecnologías Pills */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-editorial-muted mr-1">
            Centrales:
          </span>
          {tecFilters.map((tec) => (
            <button
              key={tec}
              onClick={() => setSelectedTec(tec)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedTec === tec
                  ? 'bg-editorial-dark text-white font-semibold shadow-xs'
                  : 'bg-canvas hover:bg-canvas-muted text-editorial-dark border border-editorial-border/60'
              }`}
            >
              {tec}
            </button>
          ))}
        </div>

        {/* Selector de Provincia */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-editorial-muted">
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
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-canvas border border-editorial-border text-editorial-dark focus:outline-none focus:ring-1 focus:ring-accent-indigo"
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

      {/* Main Grid: Mapa GIS (2/3) + Panel Provincia Destacada (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaflet Map Container */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-4 border border-editorial-border/80 shadow-2xs flex flex-col">
          <div className="flex items-center justify-between mb-3 px-2">
            <div>
              <span className="text-[10px] font-bold tracking-widest uppercase text-editorial-muted">
                Argentina
              </span>
              <h2 className="text-sm font-bold text-editorial-dark">
                Infraestructura energética SADI ({filteredCentrales.length} centrales activas)
              </h2>
            </div>
            <span className="text-[11px] text-editorial-muted">
              CartoDB Positron · OpenStreetMap
            </span>
          </div>

          {/* Map Viewport */}
          <div className="w-full h-[520px] rounded-xl overflow-hidden relative border border-editorial-border/50">
            <MapContainer
              center={mapState.center}
              zoom={mapState.zoom}
              scrollWheelZoom={false}
              className="w-full h-full"
            >
              <MapRecenter center={mapState.center} zoom={mapState.zoom} />
              
              {/* CartoDB Positron: capa clara y limpia para diseño editorial */}
              <TileLayer
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              />

              {/* CircleMarkers vectoriales */}
              {filteredCentrales.map((c) => {
                const color = TEC_COLORS[c.categoria_filtro] || '#3d445c';
                const radius = Math.min(Math.max(Math.sqrt(c.potencia_mw || 10) * 0.45, 3.5), 10);

                return (
                  <CircleMarker
                    key={c.id}
                    center={[c.lat, c.lon]}
                    radius={radius}
                    pathOptions={{
                      color: '#ffffff',
                      weight: 1,
                      fillColor: color,
                      fillOpacity: 0.85,
                    }}
                  >
                    <Tooltip direction="top" offset={[0, -5]} opacity={0.95}>
                      <div className="text-xs">
                        <strong className="block font-bold">{c.nombre}</strong>
                        <span>{c.categoria_filtro} · {c.potencia_mw} MW</span>
                        <div className="text-[10px] text-gray-500">{c.jurisdiccion_nombre}</div>
                      </div>
                    </Tooltip>
                    <Popup>
                      <div className="p-1 text-xs">
                        <h4 className="font-bold text-sm text-editorial-dark mb-1">{c.nombre}</h4>
                        <p><strong>Tecnología:</strong> {c.tecnologia_original}</p>
                        <p><strong>Potencia instalada:</strong> {c.potencia_mw} MW</p>
                        <p><strong>Provincia:</strong> {c.jurisdiccion_nombre}</p>
                        <button
                          onClick={() => {
                            setSelectedProvinceId(c.jurisdiccion_id);
                            setFilterProvince(String(c.jurisdiccion_id));
                          }}
                          className="mt-2 text-accent-indigo underline font-medium block"
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
          <div className="mt-3 px-3 py-2 bg-canvas/60 rounded-xl flex items-center justify-between flex-wrap gap-3 text-xs text-editorial-dark border border-editorial-border/60">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TEC_COLORS.Hidroeléctrica }} />
                <span>Hidroeléctrica</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TEC_COLORS.Eólica }} />
                <span>Eólica</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TEC_COLORS.Solar }} />
                <span>Solar</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TEC_COLORS.Térmica }} />
                <span>Térmica</span>
              </div>
            </div>
            <span className="text-[11px] text-editorial-muted">
              El tamaño del punto refleja la potencia instalada (MW)
            </span>
          </div>
        </div>

        {/* Right Panel: Provincia Destacada */}
        <div className="bg-white rounded-2xl p-6 border border-editorial-border/80 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold tracking-widest uppercase text-editorial-muted mb-1">
              Provincia destacada
            </div>
            <h2 className="text-2xl font-black text-editorial-dark tracking-tight">
              {activeProvince.nombre}
            </h2>
            <p className="text-xs text-editorial-muted mb-5">
              {activeProvince.region} · Arquetipo: <span className="font-semibold text-editorial-dark">{activeProvince.cluster?.nombre}</span>
            </p>

            {/* Score box */}
            <div className="bg-accent-sageSoft/70 rounded-2xl p-5 border border-accent-sage/30 mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-black text-editorial-dark">{scoreBase}</span>
                <span className="text-sm font-semibold text-editorial-muted">/100</span>
              </div>
              <p className="text-xs font-semibold text-accent-sageDark mt-1">
                {nivelViabilidad}
              </p>
              <p className="text-[11px] text-editorial-muted mt-2 leading-relaxed">
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
                        <span className="font-medium text-editorial-dark">{item.label}</span>
                        <span className="font-bold text-editorial-dark tabular-nums">{valRound}</span>
                      </div>
                      <div className="w-full bg-canvas rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-accent-sageDark h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(valRound, 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-editorial-border/60 text-[11px] text-editorial-muted leading-relaxed">
            Puntajes derivados de la tabla maestra auditada. Cero valores sintéticos.
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-2 text-[11px] text-editorial-muted flex flex-col sm:flex-row justify-between items-center gap-2">
        <span className="font-semibold tracking-wider uppercase text-editorial-muted/80">
          ARGENTINA · 24 JURISDICCIONES
        </span>
        <span>
          Base geográfica: Secretaría de Energía / CAMMESA · 474 centrales SADI georreferenciadas.
        </span>
      </div>
    </div>
  );
}
