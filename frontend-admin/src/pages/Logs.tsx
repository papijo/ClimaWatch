import { useEffect, useState, useCallback } from 'react'
import { getToken } from '../lib/auth'
import { getLogs, type RiskStateChange } from '../lib/api'
import RiskBadge from '../components/RiskBadge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { TableToolbar, TablePagination, SortButton, type SortConfig } from '../components/TableToolbar'

function formatDate(d: string) {
  return new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}

export default function Logs() {
  const [items, setItems] = useState<RiskStateChange[]>([])
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(10)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<SortConfig>({ key: 'changed_at', dir: 'desc' })
  const [loading, setLoading] = useState(true)
  const token = getToken()!

  const load = useCallback(async (p = page) => {
    setLoading(true)
    try {
      const res = await getLogs(token, {
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
  }, [token, search, sort.dir, limit, page])

  useEffect(() => {
    setPage(1)
    load(1)
  }, [search, sort.dir, limit]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { load(page) }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSort = (_key: string, dir: 'asc' | 'desc') => setSort({ key: 'changed_at', dir })

  return (
    <div className="p-6">
      <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 overflow-hidden">
        <TableToolbar search={search} onSearch={(v) => setSearch(v)} placeholder="Search by state name…" />

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>State</TableHead>
                <TableHead>From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>
                  <SortButton label="Date" field="changed_at" current={sort} onChange={handleSort} />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: limit }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 5 }).map((__, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground py-12">
                    {search ? 'No log entries match your search.' : 'No risk changes recorded yet.'}
                  </TableCell>
                </TableRow>
              ) : (
                items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">{item.state_name}</TableCell>
                    <TableCell><RiskBadge level={item.from_level} /></TableCell>
                    <TableCell><RiskBadge level={item.to_level} /></TableCell>
                    <TableCell className="text-muted-foreground max-w-xs truncate">{item.reason ?? '—'}</TableCell>
                    <TableCell className="text-muted-foreground">{formatDate(item.changed_at)}</TableCell>
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
