"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { api, type StateItem, type Facility } from "@/lib/api";

export default function FacilitiesPage() {
  const t = useTranslations("facilities");
  const [states, setStates] = useState<StateItem[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedState, setSelectedState] = useState("");

  useEffect(() => {
    api.getStates().then(setStates).catch(() => {});
  }, []);

  useEffect(() => {
    api.getFacilities(selectedState || undefined).then(setFacilities).catch(() => {});
  }, [selectedState]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t("title")}</h1>
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm"
        >
          <option value="">{t("filterByState")}</option>
          {states.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="py-2 pr-4">Name</th>
              <th className="py-2 pr-4">{t("lga")}</th>
              <th className="py-2 pr-4">{t("type")}</th>
              <th className="py-2 pr-4">{t("ownership")}</th>
              <th className="py-2">{t("riskScore")}</th>
            </tr>
          </thead>
          <tbody>
            {facilities.map((fac) => (
              <tr key={fac.id} className="border-b border-slate-100">
                <td className="py-2 pr-4 font-medium text-slate-900">{fac.name}</td>
                <td className="py-2 pr-4 text-slate-600">{fac.lga}</td>
                <td className="py-2 pr-4 capitalize text-slate-600">{fac.facility_type}</td>
                <td className="py-2 pr-4 capitalize text-slate-600">{fac.ownership}</td>
                <td className="py-2 font-semibold">
                  {fac.latest_risk_score?.risk_score.toFixed(1) ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
