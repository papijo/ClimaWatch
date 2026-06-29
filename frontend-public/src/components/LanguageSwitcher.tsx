"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next/navigation";
import { locales, type Locale } from "@/i18n";

const LABELS: Record<Locale, string> = {
  en: "EN",
  ha: "HA",
  yo: "YO",
  ig: "IG",
};

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: string) => {
    const segments = pathname.split("/");
    segments[1] = newLocale;
    router.push(segments.join("/"));
  };

  return (
    <select
      value={locale}
      onChange={(e) => handleChange(e.target.value)}
      className="bg-transparent text-white border border-slate-600 rounded px-2 py-1 text-xs"
    >
      {locales.map((loc) => (
        <option key={loc} value={loc} className="text-slate-900">
          {LABELS[loc]}
        </option>
      ))}
    </select>
  );
}
