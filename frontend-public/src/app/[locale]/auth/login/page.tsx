"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const t = useTranslations("auth");
  const locale = useLocale();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.login(email, password);
      setToken(res.access_token);
      router.push(`/${locale}/me/subscriptions`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">{t("loginTitle")}</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
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
          {t("loginButton")}
        </button>
      </form>

      <p className="mt-4 text-sm text-slate-500">
        {t("noAccount")}{" "}
        <Link href={`/${locale}/auth/register`} className="text-blue-600 hover:underline">
          {t("registerButton")}
        </Link>
      </p>
    </div>
  );
}
