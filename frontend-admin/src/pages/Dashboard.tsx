import { useEffect, useState } from 'react'
import { getToken } from '../lib/auth'
import { getStates, getAssessments, triggerAssessment, type StateItem, type Assessment, ApiError } from '../lib/api'
import RiskBadge from '../components/RiskBadge'

const ADVISORY_LANGS = [
  { key: 'advisory_en' as const, label: 'EN' },
  { key: 'advisory_ha' as const, label: 'HA' },
  { key: 'advisory_yo' as const, label: 'YO' },
  { key: 'advisory_ig' as const, label: 'IG' },
]

const RISK_ORDER = ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'UNKNOWN']

function formatDate(d: string | null) {
  if (!d) return 'Never assessed'
  return new Date(d).toLocaleString()
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-600 mb-1">
        <span>{label}</span>
        <span className="font-mono">{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className="h-full bg-slate-700 rounded-full" style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [states, setStates] = useState<StateItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<StateItem | null>(null)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [assessLoading, setAssessLoading] = useState(false)
  const [triggering, setTriggering] = useState(false)
  const [triggerMsg, setTriggerMsg] = useState('')

  const token = getToken()!

  useEffect(() => {
    getStates(token)
      .then(setStates)
      .finally(() => setLoading(false))
  }, [token])

  const openState = async (state: StateItem) => {
    setSelected(state)
    setAssessment(null)
    setTriggerMsg('')
    setAssessLoading(true)
    try {
      const res = await getAssessments(token, state.id)
      setAssessment(res.items[0] ?? null)
    } finally {
      setAssessLoading(false)
    }
  }

  const handleTrigger = async () => {
    if (!selected) return
    setTriggering(true)
    setTriggerMsg('')
    try {
      const res = await triggerAssessment(token, selected.id)
      setTriggerMsg(res.message)
    } catch (err) {
      setTriggerMsg(err instanceof ApiError ? err.message : 'Trigger failed')
    } finally {
      setTriggering(false)
    }
  }

  const sorted = [...states].sort(
    (a, b) => RISK_ORDER.indexOf(a.current_risk_level) - RISK_ORDER.indexOf(b.current_risk_level)
  )

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
        <span className="text-sm text-slate-400">{states.length} states / FCT</span>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {sorted.map((state) => (
            <button
              key={state.id}
              onClick={() => openState(state)}
              className="text-left bg-white border border-slate-200 rounded-lg p-4 hover:shadow-sm hover:border-slate-300 transition-all"
            >
              <p className="font-medium text-slate-900 text-sm truncate">{state.name}</p>
              <p className="text-xs text-slate-400 mt-0.5 mb-2">{state.code}</p>
              <RiskBadge level={state.current_risk_level} />
              <p className="text-xs text-slate-400 mt-2 truncate">{formatDate(state.last_assessed_at)}</p>
            </button>
          ))}
        </div>
      )}

      {selected && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-slate-200 flex items-start justify-between gap-4">
              <div>
                <h2 className="font-bold text-slate-900 text-lg">{selected.name}</h2>
                <div className="mt-1.5">
                  <RiskBadge level={selected.current_risk_level} />
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-slate-400 hover:text-slate-600 text-xl leading-none mt-0.5"
              >
                ✕
              </button>
            </div>

            <div className="px-6 py-5 space-y-6">
              {assessLoading ? (
                <p className="text-sm text-slate-500">Loading assessment…</p>
              ) : assessment ? (
                <>
                  <div className="space-y-3">
                    <ScoreBar label="Composite score" value={assessment.composite_score} />
                    <ScoreBar label="Heat stress" value={assessment.heat_stress_score} />
                    <ScoreBar label="Flood risk" value={assessment.flood_risk_score} />
                    <ScoreBar label="Disease risk" value={assessment.disease_risk_score} />
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                      Advisories
                    </p>
                    <div className="space-y-2">
                      {ADVISORY_LANGS.map(({ key, label }) => (
                        <div key={label} className="border border-slate-100 rounded-lg p-3">
                          <span className="text-xs font-bold text-slate-400 uppercase mr-2">{label}</span>
                          <span className="text-sm text-slate-700">{assessment[key]}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-slate-400">Assessed {formatDate(assessment.assessed_at)}</p>
                </>
              ) : (
                <p className="text-sm text-slate-500">No assessments yet for this state.</p>
              )}

              <div className="pt-2 border-t border-slate-100 flex items-center gap-4">
                <button
                  onClick={handleTrigger}
                  disabled={triggering}
                  className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors"
                >
                  {triggering ? 'Triggering…' : 'Trigger assessment'}
                </button>
                {triggerMsg && (
                  <p className="text-xs text-slate-600">{triggerMsg}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
