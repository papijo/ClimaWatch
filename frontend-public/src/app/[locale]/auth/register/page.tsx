"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import { api, ApiError } from "@/lib/api";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const locale = useLocale();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.register(email, password, fullName);
      router.push(`/${locale}/auth/login`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">{t("registerTitle")}</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t("fullName")}</label>
          <input
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t("email")}</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">{t("password")}</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          className="w-full bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800"
        >
          {t("registerButton")}
        </button>
      </form>

      <p className="mt-4 text-sm text-slate-500">
        {t("hasAccount")}{" "}
        <Link href={`/${locale}/auth/login`} className="text-blue-600 hover:underline">
          {t("loginButton")}
        </Link>
      </p>
    </div>
  );
}
