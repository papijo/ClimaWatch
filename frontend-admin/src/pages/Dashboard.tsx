import { useEffect, useState, useCallback } from 'react'
import { AlertOctagon, AlertTriangle, ShieldAlert, RefreshCw, X } from 'lucide-react'
import { getToken } from '../lib/auth'
import {
  getStates,
  getAssessments,
  getActiveAlerts,
  triggerAssessment,
  type StateItem,
  type Assessment,
  ApiError,
} from '../lib/api'
import RiskBadge from '../components/RiskBadge'
import AdminMap from '../components/AdminMap'
import { TablePagination } from '../components/TableToolbar'

const ADVISORY_LANGS = [
  { key: 'advisory_en' as const, label: 'English' },
  { key: 'advisory_ha' as const, label: 'Hausa' },
  { key: 'advisory_yo' as const, label: 'Yoruba' },
  { key: 'advisory_ig' as const, label: 'Igbo' },
]

const RISK_ORDER = ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'UNKNOWN']

function relativeTime(date: string | null): string {
  if (!date) return 'Never'
  const diff = Date.now() - new Date(date).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}

interface KPICardProps {
  label: string
  value: string | number
  icon: React.ElementType
  iconColor: string
  iconBg: string
}

function KPICard({ label, value, icon: Icon, iconColor, iconBg }: KPICardProps) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-wide mb-2">
            {label}
          </p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white leading-none">
            {value}
          </p>
        </div>
        <div className={`shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${iconBg}`}>
          <Icon size={18} className={iconColor} />
        </div>
      </div>
    </div>
  )
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-500 dark:text-zinc-400 mb-1">
        <span>{label}</span>
        <span className="font-mono font-medium text-slate-700 dark:text-zinc-300">
          {value.toFixed(1)}
        </span>
      </div>
      <div className="h-1.5 bg-slate-100 dark:bg-zinc-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-emerald-500 rounded-full"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [states, setStates] = useState<StateItem[]>([])
  const [alertCount, setAlertCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<StateItem | null>(null)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [assessLoading, setAssessLoading] = useState(false)
  const [triggering, setTriggering] = useState(false)
  const [triggerMsg, setTriggerMsg] = useState('')
  const [advisoryTab, setAdvisoryTab] = useState(0)
  const [tablePage, setTablePage] = useState(1)
  const [tableLimit, setTableLimit] = useState(10)

  const token = getToken()!

  useEffect(() => {
    Promise.all([
      getStates(token),
      getActiveAlerts().catch(() => []),
    ]).then(([s, a]) => {
      setStates(s)
      setAlertCount(a.length)
    }).finally(() => setLoading(false))
  }, [token])

  const openState = useCallback(async (state: StateItem) => {
    setSelected(state)
    setAssessment(null)
    setTriggerMsg('')
    setAdvisoryTab(0)
    setAssessLoading(true)
    try {
      const res = await getAssessments(token, { stateId: state.id })
      setAssessment(res.items[0] ?? null)
    } finally {
      setAssessLoading(false)
    }
  }, [token])

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
  const tableTotal = sorted.length
  const tableTotalPages = Math.max(1, Math.ceil(tableTotal / tableLimit))
  const tableRows = sorted.slice((tablePage - 1) * tableLimit, tablePage * tableLimit)

  const critical = states.filter((s) => s.current_risk_level === 'CRITICAL').length
  const high = states.filter((s) => s.current_risk_level === 'HIGH').length
  const lastRun = states.reduce((t, s) => {
    if (!s.last_assessed_at) return t
    return Math.max(t, new Date(s.last_assessed_at).getTime())
  }, 0)

  return (
    <div className="p-6 space-y-5">
      {/* KPI row */}
      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-[90px] rounded-xl bg-slate-100 dark:bg-zinc-800 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Critical states"
            value={critical}
            icon={AlertOctagon}
            iconColor="text-red-600 dark:text-red-400"
            iconBg="bg-red-50 dark:bg-red-950/50"
          />
          <KPICard
            label="High risk states"
            value={high}
            icon={AlertTriangle}
            iconColor="text-orange-600 dark:text-orange-400"
            iconBg="bg-orange-50 dark:bg-orange-950/50"
          />
          <KPICard
            label="Active alerts"
            value={alertCount}
            icon={ShieldAlert}
            iconColor="text-amber-600 dark:text-amber-400"
            iconBg="bg-amber-50 dark:bg-amber-950/50"
          />
          <KPICard
            label="Last assessment"
            value={lastRun ? relativeTime(new Date(lastRun).toISOString()) : 'Never'}
            icon={RefreshCw}
            iconColor="text-emerald-600 dark:text-emerald-400"
            iconBg="bg-emerald-50 dark:bg-emerald-950/50"
          />
        </div>
      )}

      {/* Map */}
      <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-200 dark:border-zinc-700 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
            States at a glance
          </h2>
          <span className="text-xs text-slate-400 dark:text-zinc-500">
            {states.length} states / FCT — click a marker to inspect
          </span>
        </div>
        <AdminMap
          states={states}
          onStateClick={openState}
          className="w-full h-[380px]"
        />
      </div>

      {/* State table */}
      <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-200 dark:border-zinc-700">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">All states</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 dark:border-zinc-700">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wide">
                  State
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wide">
                  Code
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wide">
                  Risk level
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wide">
                  Last assessed
                </th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: tableLimit }).map((_, i) => (
                    <tr key={i} className="border-b border-slate-50 dark:border-zinc-700/50">
                      <td colSpan={5} className="px-5 py-3">
                        <div className="h-4 bg-slate-100 dark:bg-zinc-700 rounded animate-pulse w-3/4" />
                      </td>
                    </tr>
                  ))
                : tableRows.map((state, idx) => (
                    <tr
                      key={state.id}
                      className={[
                        'border-b border-slate-50 dark:border-zinc-700/50 hover:bg-slate-50 dark:hover:bg-zinc-700/40 cursor-pointer transition-colors',
                        idx === tableRows.length - 1 ? 'border-b-0' : '',
                      ].join(' ')}
                      onClick={() => openState(state)}
                    >
                      <td className="px-5 py-3 font-medium text-slate-900 dark:text-white">
                        {state.name}
                      </td>
                      <td className="px-5 py-3 text-slate-500 dark:text-zinc-400 font-mono text-xs">
                        {state.code}
                      </td>
                      <td className="px-5 py-3">
                        <RiskBadge level={state.current_risk_level} />
                      </td>
                      <td className="px-5 py-3 text-slate-500 dark:text-zinc-400 text-xs">
                        {formatDate(state.last_assessed_at)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:underline"
                          onClick={(e) => { e.stopPropagation(); openState(state) }}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
        <TablePagination
          page={tablePage} limit={tableLimit} total={tableTotal} totalPages={tableTotalPages}
          onPageChange={setTablePage}
          onLimitChange={(l) => { setTableLimit(l); setTablePage(1) }}
        />
      </div>

      {/* State detail modal */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-white dark:bg-zinc-900 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 dark:border-zinc-700"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-zinc-700 flex items-start justify-between gap-4">
              <div>
                <h2 className="font-bold text-slate-900 dark:text-white text-lg leading-tight">
                  {selected.name}
                </h2>
                <div className="mt-2">
                  <RiskBadge level={selected.current_risk_level} />
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:text-zinc-500 dark:hover:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="px-6 py-5 space-y-6">
              {assessLoading ? (
                <div className="space-y-3">
                  {[0, 1, 2, 3].map((i) => (
                    <div key={i} className="h-5 bg-slate-100 dark:bg-zinc-800 rounded animate-pulse" />
                  ))}
                </div>
              ) : assessment ? (
                <>
                  {/* Score bars */}
                  <div className="space-y-3">
                    <ScoreBar label="Overall score" value={assessment.overall_score} />
                    <ScoreBar label="Climate score" value={assessment.climate_score} />
                    <ScoreBar label="Health score" value={assessment.health_score} />
                    <ScoreBar label="Vulnerability" value={assessment.vulnerability_score} />
                  </div>

                  {/* Advisories */}
                  <div>
                    <p className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wide mb-3">
                      Advisories
                    </p>
                    <div className="flex gap-1.5 mb-3">
                      {ADVISORY_LANGS.map(({ label }, i) => (
                        <button
                          key={label}
                          onClick={() => setAdvisoryTab(i)}
                          className={[
                            'px-3 py-1 text-xs font-medium rounded-full transition-colors',
                            advisoryTab === i
                              ? 'bg-emerald-600 text-white'
                              : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-zinc-700',
                          ].join(' ')}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                    <div className="rounded-lg border border-slate-100 dark:border-zinc-700 bg-slate-50 dark:bg-zinc-800/50 p-4 text-sm text-slate-700 dark:text-zinc-300 leading-relaxed">
                      {assessment[ADVISORY_LANGS[advisoryTab].key] || '—'}
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 dark:text-zinc-500">
                    Assessed {formatDate(assessment.assessed_at)}
                  </p>
                </>
              ) : (
                <p className="text-sm text-slate-500 dark:text-zinc-400">
                  No assessments yet for this state.
                </p>
              )}

              {/* Trigger */}
              <div className="pt-2 border-t border-slate-100 dark:border-zinc-700 flex items-center gap-4">
                <button
                  onClick={handleTrigger}
                  disabled={triggering}
                  className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-lg px-4 py-2 text-sm font-medium hover:bg-zinc-800 dark:hover:bg-zinc-100 disabled:opacity-50 transition-colors"
                >
                  {triggering ? 'Triggering…' : 'Trigger assessment'}
                </button>
                {triggerMsg && (
                  <p className="text-xs text-slate-600 dark:text-zinc-400">{triggerMsg}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
