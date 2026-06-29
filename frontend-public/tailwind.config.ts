import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        risk: {
          low: "#22c55e",
          "low-bg": "#f0fdf4",
          moderate: "#eab308",
          "moderate-bg": "#fefce8",
          high: "#f97316",
          "high-bg": "#fff7ed",
          critical: "#ef4444",
          "critical-bg": "#fef2f2",
        },
      },
    },
  },
  plugins: [],
};
export default config;
