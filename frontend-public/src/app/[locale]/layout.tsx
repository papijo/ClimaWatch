import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { NextIntlClientProvider, useMessages } from "next-intl";
import { notFound } from "next/navigation";
import { locales, type Locale } from "@/i18n";
import Navbar from "@/components/Navbar";
import AlertBanner from "@/components/AlertBanner";
import "../globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ClimaWatch — Climate-Health Intelligence for Nigeria",
  description:
    "AI-powered climate-health risk assessments, early warnings, and health facility vulnerability mapping for all 36 Nigerian states and FCT.",
};

export default function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  if (!locales.includes(locale as Locale)) notFound();

  const messages = useMessages();

  return (
    <html lang={locale}>
      <body className={inter.className}>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <AlertBanner />
          <Navbar />
          <main>{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
