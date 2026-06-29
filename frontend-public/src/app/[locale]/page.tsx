import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("home");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">{t("title")}</h1>
      <p className="text-lg text-slate-600 max-w-2xl text-center">
        {t("subtitle")}
      </p>
    </main>
  );
}
