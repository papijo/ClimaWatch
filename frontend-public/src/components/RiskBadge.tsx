"use client";

import { useTranslations } from "next-intl";
import { riskClasses } from "@/lib/risk";

export default function RiskBadge({ level }: { level: string }) {
  const t = useTranslations("risk");
  const c = riskClasses(level);

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}
    >
      {t(level as "LOW" | "MODERATE" | "HIGH" | "CRITICAL")}
    </span>
  );
}
