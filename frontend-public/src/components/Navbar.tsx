"use client";

import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Navbar() {
  const t = useTranslations("nav");
  const locale = useLocale();

  const href = (path: string) => `/${locale}${path}`;

  return (
    <nav className="bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href={href("/")} className="text-xl font-bold tracking-tight">
            ClimaWatch
          </Link>

          <div className="hidden md:flex items-center space-x-6 text-sm">
            <Link href={href("/states")} className="hover:text-slate-300">
              {t("states")}
            </Link>
            <Link href={href("/alerts")} className="hover:text-slate-300">
              {t("alerts")}
            </Link>
            <Link href={href("/disease-alerts")} className="hover:text-slate-300">
              {t("diseaseAlerts")}
            </Link>
            <Link href={href("/facilities")} className="hover:text-slate-300">
              {t("facilities")}
            </Link>
            <Link href={href("/auth/login")} className="hover:text-slate-300">
              {t("login")}
            </Link>
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </nav>
  );
}
