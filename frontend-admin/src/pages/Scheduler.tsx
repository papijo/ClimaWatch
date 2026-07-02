import { useEffect, useState } from 'react'
import { getToken } from '../lib/auth'
import { getSchedulerStatus, type SchedulerStatus } from '../lib/api'

export default function Scheduler() {
  const [jobs, setJobs] = useState<SchedulerStatus[]>([])
  const [loading, setLoading] = useState(true)

  const token = getToken()!

  const load = () => {
    setLoading(true)
    getSchedulerStatus(token)
      .then(setJobs)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [token])

  const elevated = jobs.filter((j) => j.interval_hours <= 3).length

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Scheduler Status</h1>
          {!loading && jobs.length > 0 && (
            <p className="text-sm text-slate-500 mt-0.5">
              {jobs.length} active jobs
              {elevated > 0 && (
                <span className="ml-2 text-orange-600 font-medium">
                  · {elevated} on elevated cycle
                </span>
              )}
            </p>
          )}
        </div>
        <button
          onClick={load}
          className="border border-slate-300 text-slate-700 rounded-md px-3 py-1.5 text-sm hover:bg-slate-50 transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
              <tr>
                {['State', 'Interval', 'Next run'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={3} className="px-4 py-10 text-center text-slate-400 text-sm">Loading…</td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-4 py-10 text-center text-slate-400 text-sm">
                    Scheduler not running or no jobs registered.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.state_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">{job.state_name}</td>
                    <td className="px-4 py-3 text-slate-700">
                      {job.interval_hours}h
                      {job.interval_hours <= 3 && (
                        <span className="ml-2 text-xs bg-orange-100 text-orange-700 rounded-full px-2 py-0.5 font-medium">
                          elevated
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {job.next_run_time ? new Date(job.next_run_time).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
