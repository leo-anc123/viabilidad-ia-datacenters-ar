import React from 'react';
import { useAppData } from '../../context/DataContext';
import { Database, ShieldCheck } from 'lucide-react';

export default function Header() {
  const { data, setShowFreshnessModal } = useAppData();

  // Fecha de corte o estado
  const generatedAt = data?.freshness?.generated_at_utc 
    ? new Date(data.freshness.generated_at_utc).toLocaleDateString('es-AR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    : '2026';

  const pipelineStatus = data?.freshness?.pipeline_status || 'HEALTHY';

  return (
    <header className="h-16 px-8 flex items-center justify-between border-b border-editorial-border/60 bg-canvas sticky top-0 z-10 select-none">
      {/* Brand Identity */}
      <div className="flex items-center gap-6">
        <div className="flex items-baseline gap-1.5 font-bold tracking-tight text-xl text-editorial-dark">
          <span>nodo</span>
          <span className="text-editorial-muted font-normal">/</span>
          <span className="font-extrabold">IA</span>
        </div>
        <div className="h-4 w-px bg-editorial-border" />
        <span className="text-xs font-semibold tracking-widest uppercase text-editorial-muted">
          Observatorio de Infraestructura
        </span>
      </div>

      {/* Right meta badge */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-editorial-muted">
          Argentina
        </span>

        {/* Dynamic Freshness Pill */}
        <button
          onClick={() => setShowFreshnessModal(true)}
          title="Ver trazabilidad de fuentes oficiales auditadas"
          className="group flex items-center gap-2 px-3 py-1.5 rounded-full bg-editorial-light hover:bg-canvas-muted text-editorial-dark border border-editorial-border/70 text-xs font-medium transition-all shadow-2xs"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          <span className="text-editorial-muted">Auditado ·</span>
          <span className="font-semibold text-editorial-dark">{generatedAt}</span>
          <ShieldCheck className="w-3.5 h-3.5 text-accent-sageDark ml-0.5 opacity-70 group-hover:opacity-100 transition-opacity" />
        </button>
      </div>
    </header>
  );
}
