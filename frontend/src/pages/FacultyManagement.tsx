import { useEffect, useState } from 'react'
import { facultyApi, type Faculty, type FacultyWithAvailability } from '../services/api'

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export default function FacultyManagement() {
  const [list, setList] = useState<Faculty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', email: '' })
  const [editing, setEditing] = useState<Faculty | null>(null)
  const [detail, setDetail] = useState<FacultyWithAvailability | null>(null)
  const [availabilityForm, setAvailabilityForm] = useState<{ day: number; slot: number; is_available: boolean }[]>([])

  const load = () => {
    setLoading(true)
    facultyApi.list().then(setList).catch(() => setList([])).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) return
    facultyApi.create({ name: form.name.trim(), email: form.email.trim() || undefined })
      .then(() => { setForm({ name: '', email: '' }); load() })
      .catch((err) => alert(err.message))
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editing || !form.name.trim()) return
    facultyApi.update(editing.id, { name: form.name.trim(), email: form.email.trim() || undefined })
      .then(() => { setEditing(null); setForm({ name: '', email: '' }); load() })
      .catch((err) => alert(err.message))
  }

  const openEdit = (f: Faculty) => {
    setEditing(f)
    setForm({ name: f.name, email: f.email || '' })
  }

  const openDetail = (id: number) => {
    facultyApi.get(id).then((d) => {
      setDetail(d)
      setAvailabilityForm(d.availability.map((a) => ({ day: a.day, slot: a.slot, is_available: a.is_available })))
    }).catch((err) => alert(err.message))
  }

  const saveAvailability = () => {
    if (!detail) return
    facultyApi.setAvailability(detail.id, availabilityForm)
      .then(() => openDetail(detail.id))
      .catch((err) => alert(err.message))
  }

  const addAvailabilitySlot = () => {
    setAvailabilityForm([...availabilityForm, { day: 0, slot: 0, is_available: true }])
  }

  const removeAvailabilitySlot = (i: number) => {
    setAvailabilityForm(availabilityForm.filter((_, idx) => idx !== i))
  }

  const updateAvailabilitySlot = (i: number, field: 'day' | 'slot' | 'is_available', value: number | boolean) => {
    const next = [...availabilityForm]
    if (field === 'day') next[i] = { ...next[i], day: value as number }
    else if (field === 'slot') next[i] = { ...next[i], slot: value as number }
    else next[i] = { ...next[i], is_available: value as boolean }
    setAvailabilityForm(next)
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800 mb-2">Faculty Management</h1>
      <p className="text-slate-600 mb-6">Add faculty and define their availability (day + slot).</p>

      <form onSubmit={editing ? handleUpdate : handleCreate} className="bg-white border border-slate-200 rounded-lg p-4 mb-6 shadow-sm">
        <h2 className="font-medium text-slate-700 mb-3">{editing ? 'Edit faculty' : 'Add faculty'}</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="border border-slate-300 rounded px-3 py-2 w-48"
              placeholder="Dr. Smith"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Email (optional)</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className="border border-slate-300 rounded px-3 py-2 w-56"
              placeholder="smith@school.edu"
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-primary-700 text-white rounded font-medium hover:bg-primary-800">
            {editing ? 'Update' : 'Add'}
          </button>
          {editing && (
            <button type="button" onClick={() => { setEditing(null); setForm({ name: '', email: '' }); }} className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50">
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <h2 className="font-medium text-slate-700 p-4 border-b border-slate-200">Faculty list</h2>
        {loading ? (
          <p className="p-4 text-slate-500">Loading…</p>
        ) : list.length === 0 ? (
          <p className="p-4 text-slate-500">No faculty yet. Add one above.</p>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 text-left text-sm text-slate-600">
              <tr>
                <th className="p-3">Name</th>
                <th className="p-3">Email</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.map((f) => (
                <tr key={f.id} className="border-t border-slate-100">
                  <td className="p-3">{f.name}</td>
                  <td className="p-3 text-slate-600">{f.email || '—'}</td>
                  <td className="p-3">
                    <button type="button" onClick={() => openDetail(f.id)} className="text-primary-700 font-medium mr-3 hover:underline">Availability</button>
                    <button type="button" onClick={() => openEdit(f)} className="text-slate-600 hover:underline mr-3">Edit</button>
                    <button
                      type="button"
                      onClick={() => { if (confirm('Delete this faculty?')) facultyApi.delete(f.id).then(load).catch((err) => alert(err.message)); }}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {detail && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-10 p-4" onClick={() => setDetail(null)}>
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-semibold text-slate-800 mb-2">Availability – {detail.name}</h3>
            <p className="text-sm text-slate-600 mb-4">Define which (day, slot) this faculty is available. Day: 0=Mon, 1=Tue, … Slot: 0, 1, 2, …</p>
            {availabilityForm.map((av, i) => (
              <div key={i} className="flex gap-2 items-center mb-2">
                <select
                  value={av.day}
                  onChange={(e) => updateAvailabilitySlot(i, 'day', Number(e.target.value))}
                  className="border rounded px-2 py-1"
                >
                  {DAY_NAMES.map((d, idx) => (
                    <option key={d} value={idx}>{d}</option>
                  ))}
                </select>
                <input
                  type="number"
                  min={0}
                  value={av.slot}
                  onChange={(e) => updateAvailabilitySlot(i, 'slot', Number(e.target.value))}
                  className="border rounded px-2 py-1 w-16"
                />
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={av.is_available}
                    onChange={(e) => updateAvailabilitySlot(i, 'is_available', e.target.checked)}
                  />
                  Available
                </label>
                <button type="button" onClick={() => removeAvailabilitySlot(i)} className="text-red-600 text-sm">Remove</button>
              </div>
            ))}
            <div className="flex gap-2 mt-4">
              <button type="button" onClick={addAvailabilitySlot} className="px-3 py-1 border border-slate-300 rounded text-sm">+ Add slot</button>
              <button type="button" onClick={saveAvailability} className="px-4 py-2 bg-primary-700 text-white rounded font-medium">Save availability</button>
              <button type="button" onClick={() => setDetail(null)} className="px-4 py-2 border rounded">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
