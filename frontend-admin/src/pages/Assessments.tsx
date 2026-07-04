import { useEffect, useState } from 'react'
import { getToken } from '../lib/auth'
import { getStates, getAssessments, type StateItem, type Assessment } from '../lib/api'
import RiskBadge from '../components/RiskBadge'

export default function Assessments() {
  const [states, setStates] = useState<StateItem[]>([])
  const [stateId, setStateId] = useState('')
  const [items, setItems] = useState<Assessment[]>([])
  const [cursor, setCursor] = useState<string | null>(null)
  const [prevCursors, setPrevCursors] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const token = getToken()!

  const load = async (sid?: string, c?: string) => {
    setLoading(true)
    try {
      const res = await getAssessments(token, sid, c)
      setItems(res.items)
      setCursor(res.next_cursor)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getStates(token).then(setStates)
    load()
  }, [token])

  const handleFilter = () => {
    setPrevCursors([])
    load(stateId || undefined)
  }

  const next = () => {
    if (!cursor) return
    setPrevCursors((p) => [...p, cursor])
    load(stateId || undefined, cursor)
  }

  const prev = () => {
    const stack = [...prevCursors]
    const c = stack.pop()
    setPrevCursors(stack)
    load(stateId || undefined, c)
  }

  const stateName = (id: string) => states.find((s) => s.id === id)?.name ?? id

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-slate-900 mb-6">Assessment History</h1>

      <div className="flex gap-3 mb-6">
        <select
          value={stateId}
          onChange={(e) => setStateId(e.target.value)}
          className="border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
        >
          <option value="">All states</option>
          {states.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        <button
          onClick={handleFilter}
          className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          Filter
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
              <tr>
                {['State', 'Risk', 'Overall', 'Climate', 'Health', 'Vulnerability', 'Date'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-400 text-sm">Loading…</td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-400 text-sm">No assessments found.</td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900 whitespace-nowrap">
                      {stateName(item.state_id)}
                    </td>
                    <td className="px-4 py-3"><RiskBadge level={item.risk_level} /></td>
                    <td className="px-4 py-3 font-mono text-slate-700">{item.overall_score.toFixed(1)}</td>
                    <td className="px-4 py-3 font-mono text-slate-700">{item.climate_score.toFixed(1)}</td>
                    <td className="px-4 py-3 font-mono text-slate-700">{item.health_score.toFixed(1)}</td>
                    <td className="px-4 py-3 font-mono text-slate-700">{item.vulnerability_score.toFixed(1)}</td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {new Date(item.assessed_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="px-4 py-3 border-t border-slate-100 flex justify-between">
          <button
            onClick={prev}
            disabled={prevCursors.length === 0}
            className="text-sm text-slate-600 hover:text-slate-900 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <button
            onClick={next}
            disabled={!cursor}
            className="text-sm text-slate-600 hover:text-slate-900 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}
