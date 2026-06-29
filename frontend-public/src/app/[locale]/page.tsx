"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
import dynamic from "next/dynamic";
import MapLegend from "@/components/MapLegend";
import { api, type StateItem } from "@/lib/api";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

export default function HomePage() {
  const t = useTranslations("home");
  const locale = useLocale();
  const router = useRouter();
  const [states, setStates] = useState<StateItem[]>([]);

  useEffect(() => {
    api.getStates().then(setStates).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col">
      <div className="relative">
        <Map
          className="w-full h-[calc(100vh-4rem)]"
          states={states}
          onStateClick={(id) => router.push(`/${locale}/states/${id}`)}
        />
        <MapLegend />
      </div>

      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-3">{t("title")}</h1>
        <p className="text-lg text-slate-600">{t("subtitle")}</p>
      </div>
    </div>
  );
}
