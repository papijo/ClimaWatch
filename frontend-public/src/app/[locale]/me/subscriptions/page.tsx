"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
import { api, type StateItem, type Subscription } from "@/lib/api";
import { getToken, isLoggedIn } from "@/lib/auth";

export default function SubscriptionsPage() {
  const t = useTranslations("subscriptions");
  const locale = useLocale();
  const router = useRouter();
  const [states, setStates] = useState<StateItem[]>([]);
  const [subs, setSubs] = useState<Subscription[]>([]);
  const [selectedState, setSelectedState] = useState("");
  const [prefs, setPrefs] = useState({ notify_moderate: false, notify_high: true, notify_critical: true });

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push(`/${locale}/auth/login`);
      return;
    }
    const token = getToken()!;
    api.getStates().then(setStates).catch(() => {});
    api.getSubscriptions(token).then(setSubs).catch(() => {});
  }, [locale, router]);

  const handleSubscribe = async () => {
    if (!selectedState) return;
    const token = getToken()!;
    await api.subscribe(token, selectedState, prefs);
    setSubs(await api.getSubscriptions(token));
    setSelectedState("");
  };

  const handleUnsubscribe = async (stateId: string) => {
    const token = getToken()!;
    await api.unsubscribe(token, stateId);
    setSubs(await api.getSubscriptions(token));
  };

  const stateName = (id: string) => states.find((s) => s.id === id)?.name ?? id;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">{t("title")}</h1>

      <div className="border border-slate-200 rounded-lg p-4 mb-6 space-y-3">
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">{t("selectState")}</option>
          {states.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>

        <div className="flex flex-wrap gap-4 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={prefs.notify_moderate}
              onChange={(e) => setPrefs({ ...prefs, notify_moderate: e.target.checked })}
            />
            {t("notifyModerate")}
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={prefs.notify_high}
              onChange={(e) => setPrefs({ ...prefs, notify_high: e.target.checked })}
            />
            {t("notifyHigh")}
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={prefs.notify_critical}
              onChange={(e) => setPrefs({ ...prefs, notify_critical: e.target.checked })}
            />
            {t("notifyCritical")}
          </label>
        </div>

        <button
          onClick={handleSubscribe}
          disabled={!selectedState}
          className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800 disabled:opacity-50"
        >
          {t("subscribe")}
        </button>
      </div>

      {subs.length === 0 ? (
        <p className="text-slate-500">{t("noSubscriptions")}</p>
      ) : (
        <div className="space-y-2">
          {subs.map((sub) => (
            <div key={sub.id} className="flex items-center justify-between border border-slate-200 rounded-lg p-3">
              <div>
                <p className="font-medium text-slate-900">{stateName(sub.state_id)}</p>
                <p className="text-xs text-slate-500">
                  {sub.notify_moderate && "Moderate "}{sub.notify_high && "High "}{sub.notify_critical && "Critical"}
                </p>
              </div>
              <button
                onClick={() => handleUnsubscribe(sub.state_id)}
                className="text-sm text-red-600 hover:underline"
              >
                {t("unsubscribe")}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
