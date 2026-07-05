import { useEffect, useState, useCallback } from 'react'
import { getToken } from '../lib/auth'
import { getStates, getAssessments, type StateItem, type Assessment } from '../lib/api'
import RiskBadge from '../components/RiskBadge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { TableToolbar, TablePagination, SortButton, type SortConfig } from '../components/TableToolbar'

function formatDate(d: string) {
  return new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}

export default function Assessments() {
  const [states, setStates] = useState<StateItem[]>([])
  const [stateId, setStateId] = useState('')
  const [items, setItems] = useState<Assessment[]>([])
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(10)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<SortConfig>({ key: 'assessed_at', dir: 'desc' })
  const [loading, setLoading] = useState(true)
  const token = getToken()!

  const load = useCallback(async (p = page) => {
    setLoading(true)
    try {
      const res = await getAssessments(token, {
        stateId: stateId || undefined,
        search: search || undefined,
        sortDir: sort.dir,
        page: p,
        limit,
      })
      setItems(res.items)
      setTotal(res.total)
      setTotalPages(res.total_pages)
    } finally {
      setLoading(false)
    }
  }, [token, stateId, search, sort.dir, limit, page])

  useEffect(() => { getStates(token).then(setStates) }, [token])

  useEffect(() => {
    setPage(1)
    load(1)
  }, [stateId, search, sort.dir, limit]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { load(page) }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSort = (_key: string, dir: 'asc' | 'desc') => setSort({ key: 'assessed_at', dir })

  return (
    <div className="p-6">
      <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 overflow-hidden">
        <TableToolbar search={search} onSearch={(v) => setSearch(v)} placeholder="Search by state name…">
          <Select value={stateId || 'all'} onValueChange={(v) => setStateId(v === 'all' ? '' : v)}>
            <SelectTrigger className="h-8 w-44 text-sm">
              <SelectValue placeholder="All states" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All states</SelectItem>
              {states.map((s) => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </TableToolbar>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>State</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Overall</TableHead>
                <TableHead>Climate</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Vulnerability</TableHead>
                <TableHead>
                  <SortButton label="Date" field="assessed_at" current={sort} onChange={handleSort} />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: limit }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 7 }).map((__, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground py-12">No assessments found.</TableCell>
                </TableRow>
              ) : (
                items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">{item.state_name}</TableCell>
                    <TableCell><RiskBadge level={item.risk_level} /></TableCell>
                    <TableCell className="font-mono">{item.overall_score.toFixed(1)}</TableCell>
                    <TableCell className="font-mono">{item.climate_score.toFixed(1)}</TableCell>
                    <TableCell className="font-mono">{item.health_score.toFixed(1)}</TableCell>
                    <TableCell className="font-mono">{item.vulnerability_score.toFixed(1)}</TableCell>
                    <TableCell className="text-muted-foreground">{formatDate(item.assessed_at)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        <TablePagination
          page={page} limit={limit} total={total} totalPages={totalPages}
          onPageChange={setPage} onLimitChange={setLimit}
        />
      </div>
    </div>
  )
}
