import React from 'react';
import { useAppData } from '../../context/DataContext';
import { X, ExternalLink, CheckCircle2, ShieldAlert, Database } from 'lucide-react';

export default function FreshnessModal() {
  const { data, showFreshnessModal, setShowFreshnessModal } = useAppData();

  if (!showFreshnessModal) return null;

  const freshness = data?.freshness;
  const sources = freshness?.sources ? Object.entries(freshness.sources) : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-editorial-border max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-editorial-border/60 flex items-center justify-between bg-canvas/40">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent-sageSoft flex items-center justify-center text-accent-sageDark">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-editorial-dark">
                Trazabilidad de Fuentes Oficiales Auditadas
              </h3>
              <p className="text-xs text-editorial-muted">
                Pipeline v{freshness?.pipeline_version || '2.0.0'} · Estado:{' '}
                <span className="font-semibold text-emerald-700">
                  {freshness?.pipeline_status || 'HEALTHY'}
                </span>
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowFreshnessModal(false)}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-editorial-muted hover:text-editorial-dark hover:bg-canvas-muted transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Sources list */}
        <div className="p-6 overflow-y-auto space-y-3.5 divide-y divide-editorial-border/40">
          {sources.map(([key, src]) => (
            <div key={key} className="pt-3.5 first:pt-0">
              <div className="flex items-start justify-between gap-3 mb-1">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="text-sm font-semibold text-editorial-dark">
                    {src.fuente_oficial}
                  </span>
                </div>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-editorial-light border border-editorial-border text-editorial-muted capitalize">
                  {src.dimension}
                </span>
              </div>
              <p className="text-xs text-editorial-muted pl-6 mb-1.5 leading-relaxed">
                {src.notes}
              </p>
              <div className="flex items-center justify-between text-[11px] text-editorial-muted pl-6">
                <span>Corte de datos: <strong className="text-editorial-dark font-medium">{src.data_cutoff_date}</strong></span>
                {src.url && (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-accent-indigo hover:underline font-medium"
                  >
                    Fuente externa
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-canvas-muted/40 border-t border-editorial-border/60 flex items-center justify-between text-xs text-editorial-muted">
          <span>Regla de negocio: Cero datos sintéticos inventados.</span>
          <button
            onClick={() => setShowFreshnessModal(false)}
            className="px-4 py-1.5 rounded-lg bg-editorial-dark text-white font-medium hover:bg-editorial-dark/90 transition-colors"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
