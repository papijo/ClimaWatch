import { useEffect, useState } from 'react'
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

type ContactForm = Omit<GovernmentContact, 'id'>

const EMPTY: ContactForm = { state_id: '', name: '', title: '', ministry: '', phone: null, email: '' }

export default function Contacts() {
  const [states, setStates] = useState<StateItem[]>([])
  const [contacts, setContacts] = useState<GovernmentContact[]>([])
  const [editing, setEditing] = useState<GovernmentContact | null>(null)
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState<ContactForm>(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const token = getToken()!

  const reload = () => getContacts(token).then(setContacts)

  useEffect(() => {
    getStates(token).then(setStates)
    reload()
  }, [token])

  const stateName = (id: string) => states.find((s) => s.id === id)?.name ?? id

  const startAdd = () => {
    setAdding(true)
    setEditing(null)
    setForm(EMPTY)
    setError('')
  }

  const startEdit = (c: GovernmentContact) => {
    setEditing(c)
    setAdding(false)
    setForm({ state_id: c.state_id, name: c.name, title: c.title, ministry: c.ministry, phone: c.phone, email: c.email })
    setError('')
  }

  const cancel = () => {
    setAdding(false)
    setEditing(null)
  }

  const save = async () => {
    if (!form.state_id || !form.name || !form.title || !form.ministry || !form.email) {
      setError('State, name, title, ministry, and email are required.')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (editing) {
        await updateContact(token, editing.id, form)
      } else {
        await createContact(token, form)
      }
      await reload()
      cancel()
    } catch {
      setError('Save failed. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: string) => {
    if (!confirm('Delete this contact?')) return
    await deleteContact(token, id)
    await reload()
  }

  const textField = (
    key: keyof ContactForm,
    label: string,
    type = 'text',
    required = false,
  ) => (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <input
        type={type}
        value={(form[key] as string) ?? ''}
        onChange={(e) => setForm({ ...form, [key]: e.target.value || null })}
        className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      />
    </div>
  )

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-900">Government Contacts</h1>
        <button
          onClick={startAdd}
          className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          Add contact
        </button>
      </div>

      {(adding || editing) && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">
            {editing ? 'Edit contact' : 'New contact'}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                State<span className="text-red-500 ml-0.5">*</span>
              </label>
              <select
                value={form.state_id}
                onChange={(e) => setForm({ ...form, state_id: e.target.value })}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              >
                <option value="">Select state</option>
                {states.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            {textField('name', 'Full name', 'text', true)}
            {textField('title', 'Title / designation', 'text', true)}
            {textField('ministry', 'Ministry', 'text', true)}
            {textField('email', 'Email', 'email', true)}
            {textField('phone', 'Phone')}
          </div>
          {error && <p className="text-xs text-red-600 mb-3">{error}</p>}
          <div className="flex items-center gap-3">
            <button
              onClick={save}
              disabled={saving}
              className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Create'}
            </button>
            <button onClick={cancel} className="text-sm text-slate-500 hover:text-slate-700">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
              <tr>
                {['State', 'Name', 'Title', 'Ministry', 'Phone', 'Email', ''].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {contacts.map((c) => (
                <tr key={c.id} className={editing?.id === c.id ? 'bg-blue-50' : 'hover:bg-slate-50'}>
                  <td className="px-4 py-3 text-slate-700 whitespace-nowrap">{stateName(c.state_id)}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">{c.name}</td>
                  <td className="px-4 py-3 text-slate-600">{c.title}</td>
                  <td className="px-4 py-3 text-slate-600">{c.ministry}</td>
                  <td className="px-4 py-3 text-slate-600">{c.phone ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-600">{c.email}</td>
                  <td className="px-4 py-3 text-right whitespace-nowrap space-x-3">
                    <button onClick={() => startEdit(c)} className="text-blue-600 hover:underline text-xs">
                      Edit
                    </button>
                    <button onClick={() => remove(c.id)} className="text-red-600 hover:underline text-xs">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {contacts.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-400 text-sm">
                    No contacts yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
