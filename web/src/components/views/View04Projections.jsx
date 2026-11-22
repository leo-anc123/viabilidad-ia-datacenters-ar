import React from 'react';

export default function View04Projections() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-200">
      <div>
        <div className="text-xs font-bold tracking-widest text-accent-indigo uppercase mb-1.5">
          Inteligencia Territorial / 04
        </div>
        <h1 className="text-3xl font-extrabold text-editorial-dark tracking-tight">
          Una mirada hacia el futuro
        </h1>
        <p className="text-sm text-editorial-muted mt-1 max-w-2xl">
          Compará la evolución del índice de viabilidad bajo tres escenarios de desarrollo (2026–2036).
        </p>
      </div>

      <div className="bg-white rounded-2xl p-12 border border-editorial-border/80 shadow-2xs text-center">
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-accent-sageSoft text-accent-sageDark">
          Programada para Checkpoint 2
        </span>
        <h3 className="text-lg font-bold text-editorial-dark mt-4">
          Módulo de Proyecciones Temporales 2026–2036
        </h3>
        <p className="text-xs text-editorial-muted mt-2 max-w-md mx-auto">
          Esta vista se activará formalmente en el Checkpoint 2 con los 3 escenarios oficiales (Acelerado, Tendencial, Conservador) y selector de horizonte.
        </p>
      </div>
    </div>
  );
}
