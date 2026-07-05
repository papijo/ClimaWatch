import { Search, ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

export interface SortConfig {
  key: string
  dir: 'asc' | 'desc'
}

// ── Search toolbar ─────────────────────────────────────────────────────────────

interface ToolbarProps {
  search: string
  onSearch: (v: string) => void
  placeholder?: string
  children?: React.ReactNode
}

export function TableToolbar({ search, onSearch, placeholder = 'Search…', children }: ToolbarProps) {
  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-200 dark:border-zinc-700">
      <div className="relative w-64">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={14} />
        <Input
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder={placeholder}
          className="pl-8 h-8 text-sm"
        />
      </div>
      <div className="flex items-center gap-2">{children}</div>
    </div>
  )
}

// ── Sortable column header button ──────────────────────────────────────────────

interface SortButtonProps {
  label: string
  field: string
  current: SortConfig
  onChange: (field: string, dir: 'asc' | 'desc') => void
}

export function SortButton({ label, field, current, onChange }: SortButtonProps) {
  const active = current.key === field
  const toggle = () => {
    if (!active) onChange(field, 'asc')
    else onChange(field, current.dir === 'asc' ? 'desc' : 'asc')
  }
  return (
    <button
      onClick={toggle}
      className="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground hover:text-foreground transition-colors"
    >
      {label}
      {active ? (
        current.dir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
      ) : (
        <ChevronsUpDown size={12} className="opacity-40" />
      )}
    </button>
  )
}

// ── Pagination ─────────────────────────────────────────────────────────────────

function getPageNumbers(page: number, total: number): (number | null)[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const pages = new Set<number>()
  pages.add(1)
  pages.add(total)
  for (let i = Math.max(2, page - 2); i <= Math.min(total - 1, page + 2); i++) pages.add(i)

  const sorted = [...pages].sort((a, b) => a - b)
  const result: (number | null)[] = []
  let prev = 0
  for (const p of sorted) {
    if (p - prev > 1) result.push(null)
    result.push(p)
    prev = p
  }
  return result
}

interface PaginationProps {
  page: number
  limit: number
  total: number
  totalPages: number
  onPageChange: (page: number) => void
  onLimitChange: (limit: number) => void
}

const PAGE_SIZE_OPTIONS = ['10', '20', '50', '100']

export function TablePagination({ page, limit, total, totalPages, onPageChange, onLimitChange }: PaginationProps) {
  const from = total === 0 ? 0 : (page - 1) * limit + 1
  const to = Math.min(page * limit, total)
  const pageNumbers = getPageNumbers(page, totalPages)

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 px-4 py-3 border-t border-slate-200 dark:border-zinc-700 text-sm">
      {/* Rows per page */}
      <div className="flex items-center gap-2">
        <span className="text-muted-foreground text-xs whitespace-nowrap">Rows per page</span>
        <Select value={String(limit)} onValueChange={(v) => { onLimitChange(Number(v)); onPageChange(1) }}>
          <SelectTrigger className="h-7 w-[70px] text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PAGE_SIZE_OPTIONS.map((o) => (
              <SelectItem key={o} value={o} className="text-xs">{o}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Count */}
      <span className="text-xs text-muted-foreground">
        {from}–{to} of {total.toLocaleString()}
      </span>

      {/* Page navigation */}
      <div className="flex items-center gap-1">
        <Button
          variant="outline" size="icon"
          className="h-7 w-7"
          disabled={page <= 1}
          onClick={() => onPageChange(1)}
          title="First page"
        >
          <ChevronsLeft size={13} />
        </Button>
        <Button
          variant="outline" size="icon"
          className="h-7 w-7"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          title="Previous page"
        >
          <ChevronLeft size={13} />
        </Button>

        {pageNumbers.map((p, i) =>
          p === null ? (
            <span key={`ellipsis-${i}`} className="w-7 text-center text-xs text-muted-foreground select-none">
              …
            </span>
          ) : (
            <Button
              key={p}
              variant={p === page ? 'default' : 'outline'}
              size="icon"
              className="h-7 w-7 text-xs"
              onClick={() => onPageChange(p)}
            >
              {p}
            </Button>
          )
        )}

        <Button
          variant="outline" size="icon"
          className="h-7 w-7"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          title="Next page"
        >
          <ChevronRight size={13} />
        </Button>
        <Button
          variant="outline" size="icon"
          className="h-7 w-7"
          disabled={page >= totalPages}
          onClick={() => onPageChange(totalPages)}
          title="Last page"
        >
          <ChevronsRight size={13} />
        </Button>
      </div>
    </div>
  )
}
