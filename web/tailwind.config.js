/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#0B0E17',     // Lienzo nocturno sobrio
          muted: '#101422',       // Fondos secundarios
          surface: '#131826',     // Superficie de tarjetas
          card: '#131826',        // Tarjetas
        },
        sidebar: {
          bg: '#080A12',          // Sidebar ultra profundo
          surface: '#121727',     // Hover / elementos dentro del sidebar
          border: '#1E2538',      // Borde del sidebar
          active: '#38BDF8',      // Píldora activa cian
          activeText: '#080A12',  // Texto sobre píldora activa
          muted: '#64748B'        // Texto muted del sidebar
        },
        editorial: {
          dark: '#F1F5F9',        // Títulos y cifras destacadas en modo nocturno
          subtitle: '#CBD5E1',    // Subtítulos
          body: '#94A3B8',        // Texto de cuerpo
          muted: '#64748B',       // Metadatos
          light: '#171E30',       // Chips y badges neutros
          border: '#232B3E'       // Bordes nítidos de tarjetas
        },
        accent: {
          cyan: '#38BDF8',
          emerald: '#34D399',
          amber: '#FBBF24',
          purple: '#A78BFA',
          sage: '#34D399',
          sageSoft: '#132822',
          sageDark: '#059669',
          indigo: '#38BDF8',
          indigoDark: '#0284C7',
          indigoMuted: '#1E3A5F'
        },
        heatmap: {
          highBg: '#132B24',
          highText: '#34D399',
          medBg: '#132338',
          medText: '#38BDF8',
          lowBg: '#33171D',
          lowText: '#F87171'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
