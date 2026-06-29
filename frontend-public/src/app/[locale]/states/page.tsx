"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import RiskBadge from "@/components/RiskBadge";
import { api, type StateItem } from "@/lib/api";

type SortKey = "name" | "risk";
const RISK_ORDER: Record<string, number> = { CRITICAL: 0, HIGH: 1, MODERATE: 2, LOW: 3 };

export default function StatesPage() {
  const t = useTranslations("states");
  const locale = useLocale();
  const [states, setStates] = useState<StateItem[]>([]);
  const [sort, setSort] = useState<SortKey>("name");

  useEffect(() => {
    api.getStates().then(setStates).catch(() => {});
  }, []);

  const sorted = [...states].sort((a, b) => {
    if (sort === "risk") {
      return (RISK_ORDER[a.current_risk_level] ?? 4) - (RISK_ORDER[b.current_risk_level] ?? 4);
    }
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t("title")}</h1>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm"
        >
          <option value="name">A-Z</option>
          <option value="risk">{t("riskLevel")}</option>
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sorted.map((state) => (
          <Link
            key={state.id}
            href={`/${locale}/states/${state.id}`}
            className="block border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold text-slate-900">{state.name}</h2>
              <RiskBadge level={state.current_risk_level} />
            </div>
            <p className="text-sm text-slate-500">
              {t("region")}: {state.region}
            </p>
            <p className="text-sm text-slate-500">
              {t("capital")}: {state.capital}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
