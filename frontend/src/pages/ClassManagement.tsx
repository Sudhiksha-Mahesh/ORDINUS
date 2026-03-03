import { useEffect, useState } from 'react'
import { classApi, type Class } from '../services/api'

export default function ClassManagement() {
  const [list, setList] = useState<Class[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', working_days: 5, slots_per_day: 8 })
  const [editing, setEditing] = useState<Class | null>(null)

  const load = () => {
    setLoading(true)
    classApi.list().then(setList).catch(() => setList([])).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) return
    classApi.create(form)
      .then(() => { setForm({ name: '', working_days: 5, slots_per_day: 8 }); load() })
      .catch((err) => alert(err.message))
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editing) return
    classApi.update(editing.id, form)
      .then(() => { setEditing(null); setForm({ name: '', working_days: 5, slots_per_day: 8 }); load() })
      .catch((err) => alert(err.message))
  }

  const openEdit = (c: Class) => {
    setEditing(c)
    setForm({ name: c.name, working_days: c.working_days, slots_per_day: c.slots_per_day })
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800 mb-2">Class Management</h1>
      <p className="text-slate-600 mb-6">Add classes and set working days and slots per day.</p>

      <form onSubmit={editing ? handleUpdate : handleCreate} className="bg-white border border-slate-200 rounded-lg p-4 mb-6 shadow-sm">
        <h2 className="font-medium text-slate-700 mb-3">{editing ? 'Edit class' : 'Add class'}</h2>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="border border-slate-300 rounded px-3 py-2 w-32"
              placeholder="SS1"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Working days</label>
            <input
              type="number"
              min={1}
              max={7}
              value={form.working_days}
              onChange={(e) => setForm((f) => ({ ...f, working_days: Number(e.target.value) }))}
              className="border border-slate-300 rounded px-3 py-2 w-24"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Slots per day</label>
            <input
              type="number"
              min={1}
              max={20}
              value={form.slots_per_day}
              onChange={(e) => setForm((f) => ({ ...f, slots_per_day: Number(e.target.value) }))}
              className="border border-slate-300 rounded px-3 py-2 w-24"
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-primary-700 text-white rounded font-medium hover:bg-primary-800">
            {editing ? 'Update' : 'Add'}
          </button>
          {editing && (
            <button type="button" onClick={() => { setEditing(null); setForm({ name: '', working_days: 5, slots_per_day: 8 }); }} className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50">
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <h2 className="font-medium text-slate-700 p-4 border-b border-slate-200">Classes</h2>
        {loading ? (
          <p className="p-4 text-slate-500">Loading…</p>
        ) : list.length === 0 ? (
          <p className="p-4 text-slate-500">No classes yet. Add one above.</p>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 text-left text-sm text-slate-600">
              <tr>
                <th className="p-3">Name</th>
                <th className="p-3">Working days</th>
                <th className="p-3">Slots per day</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.map((c) => (
                <tr key={c.id} className="border-t border-slate-100">
                  <td className="p-3">{c.name}</td>
                  <td className="p-3">{c.working_days}</td>
                  <td className="p-3">{c.slots_per_day}</td>
                  <td className="p-3">
                    <button type="button" onClick={() => openEdit(c)} className="text-primary-700 font-medium hover:underline mr-3">Edit</button>
                    <button
                      type="button"
                      onClick={() => { if (confirm('Delete this class?')) classApi.delete(c.id).then(load).catch((err) => alert(err.message)); }}
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
    </div>
  )
}
