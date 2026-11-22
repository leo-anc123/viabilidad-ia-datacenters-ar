import React, { createContext, useContext, useState, useEffect } from 'react';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Perfil global seleccionado: 'campus_ia_training' | 'nodo_inferencia_edge' | 'benchmark_cabase'
  const [activePerfil, setActivePerfil] = useState('campus_ia_training');
  
  // Provincia activa para inspección (por defecto 58: Neuquén o primera líder)
  const [selectedProvinceId, setSelectedProvinceId] = useState(58);

  // Control del modal de fuentes oficiales
  const [showFreshnessModal, setShowFreshnessModal] = useState(false);

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}data/ivid_payload.json`;
    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error HTTP ${res.status}: ${res.statusText}`);
        }
        return res.json();
      })
      .then((json) => {
        setData(json);
        // Establecer provincia líder del perfil si está disponible
        if (json?.kpis_por_perfil?.[activePerfil]?.top1_id) {
          setSelectedProvinceId(json.kpis_por_perfil[activePerfil].top1_id);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error cargando ivid_payload.json:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Al cambiar perfil, actualizar provincia activa a la líder de ese perfil
  const changePerfil = (newPerfil) => {
    setActivePerfil(newPerfil);
    if (data?.kpis_por_perfil?.[newPerfil]?.top1_id) {
      setSelectedProvinceId(data.kpis_por_perfil[newPerfil].top1_id);
    }
  };

  const value = {
    data,
    loading,
    error,
    activePerfil,
    changePerfil,
    selectedProvinceId,
    setSelectedProvinceId,
    showFreshnessModal,
    setShowFreshnessModal,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useAppData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useAppData debe utilizarse dentro de un DataProvider');
  }
  return context;
}
