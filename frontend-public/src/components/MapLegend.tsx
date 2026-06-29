"use client";

import { useTranslations } from "next-intl";
import { RISK_HEX } from "@/lib/risk";

const LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"] as const;

export default function MapLegend() {
  const t = useTranslations("risk");

  return (
    <div className="absolute bottom-6 left-6 bg-white/95 backdrop-blur rounded-lg shadow-lg p-3 z-10">
      <p className="text-xs font-semibold text-slate-700 mb-2">Risk Level</p>
      <div className="space-y-1.5">
        {LEVELS.map((level) => (
          <div key={level} className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: RISK_HEX[level] }}
            />
            <span className="text-xs text-slate-600">{t(level)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
