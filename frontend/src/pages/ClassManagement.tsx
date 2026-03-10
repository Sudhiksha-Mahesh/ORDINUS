import { useEffect, useState } from 'react'
import { Save, Trash2 } from 'lucide-react'
import { classApi, type Class } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, NumberInput, TextInput } from '../components/ui/Form'
import { Table, TBody, TD, TH, THead, TR } from '../components/ui/Table'

export default function ClassManagement() {
  const [list, setList] = useState<Class[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', working_days: 5, slots_per_day: 8 })
  const [editing, setEditing] = useState<Class | null>(null)
  const [submitAttempted, setSubmitAttempted] = useState(false)

  const load = () => {
    setLoading(true)
    classApi.list().then(setList).catch(() => setList([])).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitAttempted(true)
    if (!form.name.trim()) return
    classApi.create(form)
      .then(() => { setForm({ name: '', working_days: 5, slots_per_day: 8 }); load() })
      .catch((err) => alert(err.message))
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitAttempted(true)
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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Class Management</h1>
        <p className="mt-1 text-sm text-slate-600">Create classes and set working days and slots per day.</p>
      </div>

      <Card>
        <CardHeader
          title={editing ? 'Edit class' : 'Add class'}
          description="These settings define the timetable grid size for generation."
          actions={
            editing ? (
              <Button
                variant="ghost"
                onClick={() => {
                  setEditing(null)
                  setForm({ name: '', working_days: 5, slots_per_day: 8 })
                  setSubmitAttempted(false)
                }}
              >
                Cancel
              </Button>
            ) : null
          }
        />
        <CardContent className="p-6">
          <form onSubmit={editing ? handleUpdate : handleCreate} className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <Field
              label="Name"
              required
              error={submitAttempted && !form.name.trim() ? 'Name is required.' : undefined}
              className="md:col-span-1"
            >
              <TextInput
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="SS1"
                hasError={submitAttempted && !form.name.trim()}
                required
              />
            </Field>
            <Field label="Working days" hint="1–7" className="md:col-span-1">
              <NumberInput
                min={1}
                max={7}
                value={form.working_days}
                onChange={(e) => setForm((f) => ({ ...f, working_days: Number(e.target.value) }))}
              />
            </Field>
            <Field label="Slots per day" hint="1–20" className="md:col-span-1">
              <NumberInput
                min={1}
                max={20}
                value={form.slots_per_day}
                onChange={(e) => setForm((f) => ({ ...f, slots_per_day: Number(e.target.value) }))}
              />
            </Field>
            <div className="md:col-span-1 flex items-end">
              <Button type="submit" className="w-full md:w-auto">
                <Save className="h-4 w-4" />
                {editing ? 'Update' : 'Add'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Classes" description="Edit grid settings to match your academic schedule." />
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6 text-sm text-slate-600">Loading…</div>
          ) : list.length === 0 ? (
            <div className="p-6 text-sm text-slate-600">No classes yet. Add one above.</div>
          ) : (
            <Table>
              <THead>
                <tr>
                  <TH>Name</TH>
                  <TH>Working days</TH>
                  <TH>Slots/day</TH>
                  <TH className="text-right">Actions</TH>
                </tr>
              </THead>
              <TBody>
                {list.map((c) => (
                  <TR key={c.id}>
                    <TD className="font-medium text-slate-900">{c.name}</TD>
                    <TD>{c.working_days}</TD>
                    <TD>{c.slots_per_day}</TD>
                    <TD className="text-right">
                      <div className="inline-flex flex-wrap justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => openEdit(c)}>
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => {
                            if (confirm('Delete this class?')) {
                              classApi.delete(c.id).then(load).catch((err) => alert(err.message))
                            }
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </Button>
                      </div>
                    </TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
