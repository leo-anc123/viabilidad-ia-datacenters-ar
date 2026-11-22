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
          DEFAULT: '#f0eee6',
          muted: '#e7e5dc',
          surface: '#ffffff',
          card: '#faf9f5'
        },
        sidebar: {
          bg: '#181829',
          surface: '#222238',
          border: '#2a2a44',
          active: '#9bb0a8',
          activeText: '#181829',
          muted: '#8b8b9e'
        },
        editorial: {
          dark: '#2e252c',
          plum: '#3e2e38',
          muted: '#7a7077',
          light: '#f2f0ea',
          border: '#e4e1d7'
        },
        accent: {
          sage: '#9bb0a8',
          sageSoft: '#dce6e1',
          sageDark: '#365548',
          indigo: '#4c35de',
          indigoDark: '#201a3d',
          indigoMuted: '#5d5589'
        },
        heatmap: {
          highBg: '#dce9df',
          highText: '#235e35',
          medBg: '#e5eef2',
          medText: '#2a5568',
          lowBg: '#fae6e4',
          lowText: '#933834'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
      }
    },
  },
  plugins: [],
}
