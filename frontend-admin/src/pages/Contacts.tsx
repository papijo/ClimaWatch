import { useEffect, useState, useCallback } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { getToken } from '../lib/auth'
import {
  getStates,
  getContacts,
  createContact,
  updateContact,
  deleteContact,
  type StateItem,
  type GovernmentContact,
} from '../lib/api'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { TableToolbar, TablePagination, SortButton, type SortConfig } from '../components/TableToolbar'

type ContactForm = Omit<GovernmentContact, 'id' | 'state_name'>
const EMPTY: ContactForm = { state_id: '', name: '', title: '', ministry: '', phone: null, email: '' }

export default function Contacts() {
  const [states, setStates] = useState<StateItem[]>([])
  const [items, setItems] = useState<GovernmentContact[]>([])
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(10)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<SortConfig>({ key: 'state', dir: 'asc' })
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<GovernmentContact | null>(null)
  const [form, setForm] = useState<ContactForm>(EMPTY)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const token = getToken()!

  const load = useCallback(async (p = page) => {
    setLoading(true)
    try {
      const res = await getContacts(token, {
        search: search || undefined,
        sortBy: sort.key,
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
  }, [token, search, sort, limit, page])

  useEffect(() => { getStates(token).then(setStates) }, [token])

  useEffect(() => {
    setPage(1)
    load(1)
  }, [search, sort, limit]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load(page)
  }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSort = (key: string, dir: 'asc' | 'desc') => setSort({ key, dir })

  const openAdd = () => { setEditing(null); setForm(EMPTY); setFormError(''); setDialogOpen(true) }
  const openEdit = (c: GovernmentContact) => {
    setEditing(c)
    setForm({ state_id: c.state_id, name: c.name, title: c.title, ministry: c.ministry, phone: c.phone, email: c.email })
    setFormError('')
    setDialogOpen(true)
  }

  const save = async () => {
    if (!form.state_id || !form.name || !form.title || !form.ministry || !form.email) {
      setFormError('State, name, title, ministry, and email are required.')
      return
    }
    setSaving(true)
    setFormError('')
    try {
      if (editing) await updateContact(token, editing.id, form)
      else await createContact(token, form)
      setDialogOpen(false)
      load(page)
    } catch {
      setFormError('Save failed. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: string) => {
    if (!confirm('Delete this contact?')) return
    await deleteContact(token, id)
    load(page)
  }

  const field = (key: keyof ContactForm, label: string, type = 'text', required = false) => (
    <div className="space-y-1.5">
      <Label htmlFor={key}>
        {label}{required && <span className="text-destructive ml-0.5">*</span>}
      </Label>
      <Input
        id={key}
        type={type}
        value={(form[key] as string) ?? ''}
        onChange={(e) => setForm({ ...form, [key]: e.target.value || null })}
      />
    </div>
  )

  return (
    <div className="p-6">
      <div className="rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 overflow-hidden">
        <TableToolbar search={search} onSearch={(v) => setSearch(v)} placeholder="Search by name, state, ministry…">
          <Button size="sm" onClick={openAdd}>
            <Plus size={14} className="mr-1" /> Add contact
          </Button>
        </TableToolbar>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead><SortButton label="State" field="state" current={sort} onChange={handleSort} /></TableHead>
                <TableHead><SortButton label="Name" field="name" current={sort} onChange={handleSort} /></TableHead>
                <TableHead>Title</TableHead>
                <TableHead><SortButton label="Ministry" field="ministry" current={sort} onChange={handleSort} /></TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Email</TableHead>
                <TableHead />
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
                  <TableCell colSpan={7} className="text-center text-muted-foreground py-12">
                    {search ? 'No contacts match your search.' : 'No contacts yet.'}
                  </TableCell>
                </TableRow>
              ) : (
                items.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">{c.state_name}</TableCell>
                    <TableCell>{c.name}</TableCell>
                    <TableCell className="text-muted-foreground">{c.title}</TableCell>
                    <TableCell className="text-muted-foreground">{c.ministry}</TableCell>
                    <TableCell className="text-muted-foreground">{c.phone ?? '—'}</TableCell>
                    <TableCell className="text-muted-foreground">{c.email}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(c)}>
                          <Pencil size={13} />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" onClick={() => remove(c.id)}>
                          <Trash2 size={13} />
                        </Button>
                      </div>
                    </TableCell>
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

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit contact' : 'New contact'}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
            <div className="space-y-1.5 sm:col-span-2">
              <Label>State<span className="text-destructive ml-0.5">*</span></Label>
              <Select value={form.state_id} onValueChange={(v) => setForm({ ...form, state_id: v })}>
                <SelectTrigger><SelectValue placeholder="Select state" /></SelectTrigger>
                <SelectContent>
                  {states.map((s) => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            {field('name', 'Full name', 'text', true)}
            {field('title', 'Title / designation', 'text', true)}
            {field('ministry', 'Ministry', 'text', true)}
            {field('email', 'Email', 'email', true)}
            {field('phone', 'Phone')}
          </div>
          {formError && <p className="text-xs text-destructive mt-1">{formError}</p>}
          <div className="flex justify-end gap-3 mt-4">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={save} disabled={saving}>{saving ? 'Saving…' : editing ? 'Save changes' : 'Create'}</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
