"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
import dynamic from "next/dynamic";
import RiskBadge from "@/components/RiskBadge";
import { api, type StateDetail, type LGAScore, type Facility } from "@/lib/api";
import { riskClasses } from "@/lib/risk";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

type Locale = "en" | "ha" | "yo" | "ig";

export default function StateDetailPage() {
  const params = useParams();
  const stateId = params.id as string;
  const t = useTranslations("stateDetail");
  const locale = useLocale() as Locale;

  const [state, setState] = useState<StateDetail | null>(null);
  const [lgas, setLgas] = useState<LGAScore[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);

  useEffect(() => {
    api.getState(stateId).then(setState).catch(() => {});
    api.getStateLGAs(stateId).then(setLgas).catch(() => {});
    api.getFacilities(stateId).then(setFacilities).catch(() => {});
  }, [stateId]);

  if (!state) return <div className="p-8 text-center text-slate-500">{t("noAssessment")}</div>;

  const assessment = state.latest_assessment;
  const advisoryKey = `advisory_${locale}` as const;
  const advisory = assessment ? (assessment[advisoryKey] ?? assessment.advisory_en) : null;
  const rc = riskClasses(state.current_risk_level);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className={`rounded-lg p-6 border ${rc.bg} ${rc.border}`}>
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">{state.name}</h1>
          <RiskBadge level={state.current_risk_level} />
        </div>
        <p className="text-sm text-slate-500 mt-1">{state.region} — {state.capital}</p>
      </div>

      {assessment && (
        <section>
          <h2 className="text-lg font-semibold text-slate-900 mb-3">{t("latestAssessment")}</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
            {[
              { label: t("overallScore"), value: assessment.overall_score },
              { label: t("climateScore"), value: assessment.climate_score },
              { label: t("healthScore"), value: assessment.health_score },
              { label: t("vulnerabilityScore"), value: assessment.vulnerability_score },
            ].map((s) => (
              <div key={s.label} className="bg-white border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-slate-900">{s.value.toFixed(1)}</p>
                <p className="text-xs text-slate-500">{s.label}</p>
              </div>
            ))}
          </div>
          {advisory && (
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-1">{t("advisory")}</h3>
              <p className="text-sm text-slate-600">{advisory}</p>
            </div>
          )}
        </section>
      )}

      {lgas.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-slate-900 mb-3">{t("lgaBreakdown")}</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-slate-500">
                  <th className="py-2 pr-4">LGA</th>
                  <th className="py-2 pr-4">Score</th>
                  <th className="py-2 pr-4">Population</th>
                  <th className="py-2 pr-4">Health Access</th>
                  <th className="py-2">Climate</th>
                </tr>
              </thead>
              <tbody>
                {lgas.map((lga) => (
                  <tr key={lga.id} className="border-b border-slate-100">
                    <td className="py-2 pr-4 font-medium text-slate-900">{lga.lga_name}</td>
                    <td className="py-2 pr-4 font-semibold">{lga.vulnerability_score.toFixed(1)}</td>
                    <td className="py-2 pr-4">{lga.population_density_score.toFixed(1)}</td>
                    <td className="py-2 pr-4">{lga.health_access_score.toFixed(1)}</td>
                    <td className="py-2">{lga.climate_exposure_score.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {facilities.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-slate-900 mb-3">{t("healthFacilities")}</h2>

          <div className="mb-4 rounded-lg overflow-hidden border border-slate-200">
            <Map
              className="w-full h-[300px]"
              states={[{
                id: state.id,
                name: state.name,
                code: state.code,
                region: state.region,
                capital: state.capital,
                latitude: state.latitude,
                longitude: state.longitude,
                current_risk_level: state.current_risk_level,
              }]}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {facilities.slice(0, 12).map((fac) => (
              <div key={fac.id} className="border border-slate-200 rounded-lg p-3">
                <p className="font-medium text-slate-900 text-sm">{fac.name}</p>
                <p className="text-xs text-slate-500">{fac.lga} — {fac.facility_type}</p>
                {fac.latest_risk_score && (
                  <p className="text-xs font-semibold mt-1">
                    Risk: {fac.latest_risk_score.risk_score.toFixed(1)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
