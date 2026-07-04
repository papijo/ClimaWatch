import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        risk: {
          low: '#22c55e',
          moderate: '#eab308',
          high: '#f97316',
          critical: '#ef4444',
          'low-bg': '#f0fdf4',
          'moderate-bg': '#fefce8',
          'high-bg': '#fff7ed',
          'critical-bg': '#fef2f2',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
