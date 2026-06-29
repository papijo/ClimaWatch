"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useLocale } from "next-intl";
import { api, type ActiveAlert } from "@/lib/api";

export default function AlertBanner() {
  const locale = useLocale();
  const [alerts, setAlerts] = useState<ActiveAlert[]>([]);

  useEffect(() => {
    api.getActiveAlerts().then(setAlerts).catch(() => {});
  }, []);

  if (alerts.length === 0) return null;

  const latest = alerts[0];
  const bgColor = latest.risk_level === "CRITICAL" ? "bg-red-600" : "bg-orange-500";

  return (
    <div className={`${bgColor} text-white px-4 py-2 text-center text-sm`}>
      <Link href={`/${locale}/alerts`} className="underline font-medium">
        {latest.title}
      </Link>
      <span className="ml-2 opacity-80">
        +{alerts.length - 1 > 0 ? `${alerts.length - 1} more` : ""}
      </span>
    </div>
  );
}
