import React from 'react';
import { useAppData } from '../../context/DataContext';
import { ShieldCheck } from 'lucide-react';

export default function Header() {
  const { data, setShowFreshnessModal } = useAppData();

  const generatedAt = data?.freshness?.generated_at_utc 
    ? new Date(data.freshness.generated_at_utc).toLocaleDateString('es-AR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    : '2026';

  return (
    <header className="h-16 px-8 flex items-center justify-between border-b border-editorial-border bg-canvas/95 backdrop-blur-md sticky top-0 z-10 select-none">
      {/* Brand Identity */}
      <div className="flex items-center gap-6">
        <div className="flex items-baseline gap-1.5 font-bold font-display tracking-tight text-xl text-editorial-dark">
          <span>nodo</span>
          <span className="text-accent-cyan font-normal">/</span>
          <span className="font-extrabold text-accent-cyan">IA</span>
        </div>
        <div className="h-4 w-px bg-editorial-border" />
        <span className="text-xs font-bold tracking-widest uppercase text-editorial-muted font-sans">
          Observatorio de Infraestructura
        </span>
      </div>

      {/* Right meta badge */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-semibold text-editorial-subtitle">
          Argentina
        </span>

        {/* Dynamic Freshness Pill */}
        <button
          onClick={() => setShowFreshnessModal(true)}
          title="Ver trazabilidad de fuentes oficiales auditadas"
          className="group flex items-center gap-2 px-3 py-1.5 rounded-full bg-canvas-card hover:bg-canvas-muted text-editorial-dark border border-editorial-border text-xs font-semibold transition-all shadow-xs cursor-pointer"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-editorial-muted font-medium">Auditado ·</span>
          <span className="font-bold text-editorial-dark">{generatedAt}</span>
          <ShieldCheck className="w-3.5 h-3.5 text-accent-emerald ml-0.5 opacity-90 group-hover:opacity-100 transition-opacity" />
        </button>
      </div>
    </header>
  );
}
