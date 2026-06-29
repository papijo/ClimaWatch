"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { api, type DiseaseAlert } from "@/lib/api";

export default function DiseaseAlertsPage() {
  const t = useTranslations("diseaseAlerts");
  const [alerts, setAlerts] = useState<DiseaseAlert[]>([]);

  useEffect(() => {
    api.getDiseaseAlerts().then(setAlerts).catch(() => {});
  }, []);

  const levelColor: Record<string, string> = {
    watch: "bg-yellow-100 text-yellow-800",
    warning: "bg-orange-100 text-orange-800",
    emergency: "bg-red-100 text-red-800",
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">{t("title")}</h1>

      {alerts.length === 0 ? (
        <p className="text-slate-500">{t("noAlerts")}</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="border border-slate-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold text-slate-900">{alert.disease_name}</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${levelColor[alert.alert_level] ?? ""}`}>
                  {alert.alert_level}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-2">{alert.description}</p>
              <div className="flex gap-4 text-xs text-slate-400">
                <span>{t("source")}: {alert.source.toUpperCase()}</span>
                <span>{t("reportedAt")}: {new Date(alert.reported_at).toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
