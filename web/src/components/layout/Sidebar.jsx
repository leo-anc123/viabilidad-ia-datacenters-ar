import React from 'react';

const NAV_ITEMS = [
  { id: '01', key: 'dashboard', label: 'Dashboard analítico' },
  { id: '02', key: 'map', label: 'Mapa geoespacial' },
  { id: '03', key: 'simulator', label: 'Simulador interactivo' },
  { id: '04', key: 'projections', label: 'Proyecciones a futuro' },
  { id: '05', key: 'matrix', label: 'Matriz provincial' },
];

export default function Sidebar({ activeView, setActiveView }) {
  return (
    <aside className="w-64 bg-sidebar-bg text-sidebar-muted min-h-screen flex flex-col justify-between p-6 shrink-0 border-r border-sidebar-border z-20 select-none">
      <div>
        {/* PLATAFORMA Kicker */}
        <div className="text-[11px] font-semibold tracking-wider text-sidebar-muted/70 uppercase mb-6 px-3">
          Plataforma
        </div>

        {/* Navigation list */}
        <nav className="space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const isActive = activeView === item.key;
            return (
              <button
                key={item.key}
                onClick={() => setActiveView(item.key)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 text-left ${
                  isActive
                    ? 'bg-sidebar-active text-sidebar-activeText shadow-sm font-semibold'
                    : 'text-sidebar-muted hover:text-white/90 hover:bg-sidebar-surface/60'
                }`}
              >
                <span className={`text-xs tabular-nums ${isActive ? 'text-sidebar-activeText/80' : 'text-sidebar-muted/60'}`}>
                  {item.id}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Section */}
      <div className="pt-6 border-t border-sidebar-border/80">
        <div className="text-[10px] font-bold tracking-wider text-sidebar-muted/65 uppercase mb-2">
          Decisiones con evidencia
        </div>
        <p className="text-sm font-normal text-white/90 leading-snug mb-5">
          El próximo polo de IA empieza con una mejor pregunta.
        </p>
        <div className="text-[11px] text-sidebar-muted/60">
          Modelo exploratorio · v2.0.0
        </div>
      </div>
    </aside>
  );
}
