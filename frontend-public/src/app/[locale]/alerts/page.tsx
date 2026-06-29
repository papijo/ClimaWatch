"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import RiskBadge from "@/components/RiskBadge";
import { api, type ActiveAlert } from "@/lib/api";

export default function AlertsPage() {
  const t = useTranslations("alerts");
  const locale = useLocale();
  const [alerts, setAlerts] = useState<ActiveAlert[]>([]);

  useEffect(() => {
    api.getActiveAlerts().then(setAlerts).catch(() => {});
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t("title")}</h1>
        <Link
          href={`/${locale}/alerts/history`}
          className="text-sm text-blue-600 hover:underline"
        >
          {t("history")}
        </Link>
      </div>

      {alerts.length === 0 ? (
        <p className="text-slate-500">{t("noActive")}</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="border border-slate-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold text-slate-900">{alert.title}</h2>
                <RiskBadge level={alert.risk_level} />
              </div>
              <p className="text-sm text-slate-600 mb-2">{alert.description}</p>
              <p className="text-xs text-slate-400">
                {t("startedAt")}: {new Date(alert.started_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
