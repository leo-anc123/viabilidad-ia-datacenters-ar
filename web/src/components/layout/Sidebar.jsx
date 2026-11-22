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
        <div className="text-[10px] font-bold tracking-widest text-editorial-muted uppercase mb-6 px-3">
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
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 text-left ${
                  isActive
                    ? 'bg-[#162033] text-accent-cyan border border-accent-cyan/40 shadow-sm'
                    : 'text-editorial-muted hover:text-editorial-subtitle hover:bg-sidebar-surface/70'
                }`}
              >
                <span className={`text-[11px] font-mono tabular-nums ${isActive ? 'text-accent-cyan font-bold' : 'text-editorial-muted/70'}`}>
                  {item.id}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Section */}
      <div className="pt-6 border-t border-sidebar-border">
        <div className="text-[10px] font-bold tracking-widest text-editorial-muted uppercase mb-2">
          Decisiones con evidencia
        </div>
        <p className="text-xs font-medium text-editorial-subtitle leading-snug mb-4">
          El próximo polo de IA empieza con una mejor pregunta.
        </p>
        <div className="text-[11px] font-mono text-editorial-muted">
          Modelo territorial · v2.0.0
        </div>
      </div>
    </aside>
  );
}
