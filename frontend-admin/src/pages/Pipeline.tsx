import { useEffect, useState } from 'react'
import { RefreshCw, CheckCircle2, AlertCircle, Clock, Database, Wifi } from 'lucide-react'
import { getToken } from '../lib/auth'
import { getPipelineStatus, triggerPipeline, type PipelineSource, ApiError } from '../lib/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

function relativeTime(date: string | null): string {
  if (!date) return 'Never run'
  const diff = Date.now() - new Date(date).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function StatusBadge({ status }: { status: PipelineSource['status'] }) {
  if (status === 'ok') {
    return (
      <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
        <CheckCircle2 size={13} /> Operational
      </span>
    )
  }
  if (status === 'error') {
    return (
      <span className="flex items-center gap-1.5 text-xs font-medium text-red-600 dark:text-red-400">
        <AlertCircle size={13} /> Error
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1.5 text-xs font-medium text-zinc-500">
      <Clock size={13} /> Never run
    </span>
  )
}

interface SourceCardProps {
  source: PipelineSource
  onTrigger: (key: string) => void
  triggering: string | null
}

function SourceCard({ source, onTrigger, triggering }: SourceCardProps) {
  const isTriggering = triggering === source.source

  return (
    <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 p-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className={[
            'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
            source.type === 'api'
              ? 'bg-blue-50 dark:bg-blue-950/50'
              : 'bg-slate-100 dark:bg-zinc-700',
          ].join(' ')}>
            {source.type === 'api'
              ? <Wifi size={15} className="text-blue-600 dark:text-blue-400" />
              : <Database size={15} className="text-slate-500 dark:text-zinc-400" />
            }
          </div>
          <div>
            <p className="font-semibold text-sm text-slate-900 dark:text-white leading-tight">
              {source.label}
            </p>
            <Badge variant={source.type === 'api' ? 'default' : 'secondary'} className="text-[10px] mt-0.5 px-1.5 py-0">
              {source.type === 'api' ? 'Live API' : 'Dataset'}
            </Badge>
          </div>
        </div>
        <StatusBadge status={source.status} />
      </div>

      <p className="text-xs text-slate-500 dark:text-zinc-400 mb-4 leading-relaxed">
        {source.description}
      </p>

      <div className="flex items-center justify-between">
        <div className="text-xs text-slate-500 dark:text-zinc-400 space-y-0.5">
          <p>Last run: <span className="text-slate-700 dark:text-zinc-300 font-medium">{relativeTime(source.last_run)}</span></p>
          {source.records_stored > 0 && (
            <p>Records: <span className="text-slate-700 dark:text-zinc-300 font-medium">{source.records_stored.toLocaleString()}</span></p>
          )}
        </div>

        {source.can_trigger ? (
          <Button
            size="sm"
            variant="outline"
            disabled={isTriggering}
            onClick={() => onTrigger(source.source)}
          >
            <RefreshCw size={13} className={['mr-1.5', isTriggering ? 'animate-spin' : ''].join(' ')} />
            {isTriggering ? 'Running…' : 'Run now'}
          </Button>
        ) : (
          <span className="text-xs text-slate-400 dark:text-zinc-500 italic">Manual upload only</span>
        )}
      </div>
    </div>
  )
}

export default function Pipeline() {
  const [sources, setSources] = useState<PipelineSource[]>([])
  const [loading, setLoading] = useState(true)
  const [triggering, setTriggering] = useState<string | null>(null)
  const [messages, setMessages] = useState<Record<string, string>>({})
  const token = getToken()!

  const loadStatus = async () => {
    setLoading(true)
    try {
      const data = await getPipelineStatus(token)
      setSources(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStatus()
  }, [token]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleTrigger = async (key: string) => {
    setTriggering(key)
    setMessages((m) => ({ ...m, [key]: '' }))
    try {
      const res = await triggerPipeline(token, key)
      setMessages((m) => ({ ...m, [key]: res.message }))
      setTimeout(() => loadStatus(), 3000)
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Trigger failed'
      setMessages((m) => ({ ...m, [key]: msg }))
    } finally {
      setTriggering(null)
    }
  }

  const apiSources = sources.filter((s) => s.type === 'api')
  const datasetSources = sources.filter((s) => s.type === 'dataset')

  return (
    <div className="p-6 space-y-6">
      {/* API sources */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Live API Sources</h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Fetch real-time climate data for all 37 states
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            disabled={!!triggering}
            onClick={() => {
              apiSources.filter((s) => s.can_trigger).forEach((s) => handleTrigger(s.source))
            }}
          >
            <RefreshCw size={13} className={['mr-1.5', triggering ? 'animate-spin' : ''].join(' ')} />
            Run all sources
          </Button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="h-44 rounded-xl" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {apiSources.map((s) => (
              <div key={s.source}>
                <SourceCard source={s} onTrigger={handleTrigger} triggering={triggering} />
                {messages[s.source] && (
                  <p className="text-xs mt-1.5 px-1 text-slate-600 dark:text-zinc-400">
                    {messages[s.source]}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dataset sources */}
      <div>
        <div className="mb-3">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Dataset Sources</h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Ingested via upload scripts — cannot be triggered from the UI
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="h-40 rounded-xl" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {datasetSources.map((s) => (
              <SourceCard key={s.source} source={s} onTrigger={handleTrigger} triggering={triggering} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
