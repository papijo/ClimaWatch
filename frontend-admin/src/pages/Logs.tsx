import { useEffect, useState } from 'react'
import { getToken } from '../lib/auth'
import { getLogs, type RiskStateChange } from '../lib/api'
import RiskBadge from '../components/RiskBadge'

export default function Logs() {
  const [items, setItems] = useState<RiskStateChange[]>([])
  const [cursor, setCursor] = useState<string | null>(null)
  const [prevCursors, setPrevCursors] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  const token = getToken()!

  const load = async (c?: string) => {
    setLoading(true)
    try {
      const res = await getLogs(token, c)
      setItems(res.items)
      setCursor(res.next_cursor)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [token])

  const next = () => {
    if (!cursor) return
    setPrevCursors((p) => [...p, cursor])
    load(cursor)
  }

  const prev = () => {
    const stack = [...prevCursors]
    const c = stack.pop()
    setPrevCursors(stack)
    load(c)
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-slate-900 mb-6">Risk Change Logs</h1>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
              <tr>
                {['State', 'From', 'To', 'Reason', 'Date'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-slate-400 text-sm">Loading…</td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-slate-400 text-sm">No risk changes recorded yet.</td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900 whitespace-nowrap">{item.state_name}</td>
                    <td className="px-4 py-3"><RiskBadge level={item.from_level} /></td>
                    <td className="px-4 py-3"><RiskBadge level={item.to_level} /></td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{item.reason ?? '—'}</td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {new Date(item.changed_at).toLocaleString()}
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
