"use client";

import { useEffect, useState, useCallback } from "react";
import { useTranslations } from "next-intl";
import RiskBadge from "@/components/RiskBadge";
import { api, type ActiveAlert } from "@/lib/api";

export default function AlertHistoryPage() {
  const t = useTranslations("alerts");
  const [items, setItems] = useState<ActiveAlert[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    try {
      const res = await api.getAlertHistory(cursor ?? undefined);
      setItems((prev) => [...prev, ...res.items]);
      setCursor(res.next_cursor);
      setHasMore(res.next_cursor !== null);
    } catch {
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [cursor, loading, hasMore]);

  useEffect(() => {
    loadMore();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop >=
        document.documentElement.offsetHeight - 200
      ) {
        loadMore();
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [loadMore]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">{t("history")}</h1>

      <div className="space-y-3">
        {items.map((alert) => (
          <div key={alert.id} className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold text-slate-900">{alert.title}</h2>
              <RiskBadge level={alert.risk_level} />
            </div>
            <p className="text-sm text-slate-600 mb-2">{alert.description}</p>
            <div className="flex gap-4 text-xs text-slate-400">
              <span>{t("startedAt")}: {new Date(alert.started_at).toLocaleString()}</span>
              {alert.ended_at && (
                <span>{t("endedAt")}: {new Date(alert.ended_at).toLocaleString()}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {loading && <p className="text-center text-slate-500 py-4">Loading...</p>}
      {!hasMore && items.length > 0 && (
        <p className="text-center text-slate-400 py-4 text-sm">No more alerts.</p>
      )}
    </div>
  );
}
