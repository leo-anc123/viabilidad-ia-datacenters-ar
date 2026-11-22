import React, { useState } from 'react';
import { DataProvider, useAppData } from './context/DataContext';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import FreshnessModal from './components/common/FreshnessModal';
import View01Dashboard from './components/views/View01Dashboard';
import View02Map from './components/views/View02Map';
import View03Simulator from './components/views/View03Simulator';
import View04Projections from './components/views/View04Projections';
import View05Matrix from './components/views/View05Matrix';
import { Loader2, AlertCircle } from 'lucide-react';

function MainLayout() {
  const { loading, error } = useAppData();
  const [activeView, setActiveView] = useState('dashboard');

  if (loading) {
    return (
      <div className="min-h-screen bg-canvas flex flex-col items-center justify-center text-editorial-dark">
        <Loader2 className="w-8 h-8 text-sidebar-bg animate-spin mb-3" />
        <h2 className="text-lg font-bold">Cargando Observatorio de Infraestructura...</h2>
        <p className="text-xs text-editorial-muted mt-1">
          Validando contrato de datos unificado ivid_payload.json
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-canvas flex flex-col items-center justify-center p-6 text-editorial-dark">
        <div className="bg-white rounded-2xl p-8 border border-editorial-border shadow-lg max-w-md text-center">
          <AlertCircle className="w-10 h-10 text-rose-600 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-editorial-dark">Error al cargar datos</h2>
          <p className="text-xs text-editorial-muted mt-2 mb-4 leading-relaxed">
            No se pudo cargar el archivo <code>ivid_payload.json</code>. Verifique que se haya ejecutado <code>python src/pipeline/export_web_payload.py</code>.
          </p>
          <div className="text-xs font-mono bg-canvas p-2.5 rounded-lg text-rose-700 text-left overflow-x-auto">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-canvas text-editorial-dark">
      {/* Sidebar fijo lateral */}
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      {/* Área principal */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-8 overflow-y-auto">
          {activeView === 'dashboard' && <View01Dashboard onNavigate={setActiveView} />}
          {activeView === 'map' && <View02Map />}
          {activeView === 'simulator' && <View03Simulator />}
          {activeView === 'projections' && <View04Projections />}
          {activeView === 'matrix' && <View05Matrix />}
        </main>
      </div>

      {/* Modal interactivo de fuentes oficiales */}
      <FreshnessModal />
    </div>
  );
}

export default function App() {
  return (
    <DataProvider>
      <MainLayout />
    </DataProvider>
  );
}
