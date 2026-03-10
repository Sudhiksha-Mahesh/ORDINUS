import { useEffect, useState } from 'react'
import { Plus, Save, Trash2 } from 'lucide-react'
import { facultyApi, type Faculty, type FacultyWithAvailability } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Modal } from '../components/ui/Modal'
import { Field, NumberInput, Select, TextInput } from '../components/ui/Form'
import { Table, TBody, TD, TH, THead, TR } from '../components/ui/Table'

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export default function FacultyManagement() {
  const [list, setList] = useState<Faculty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', email: '' })
  const [editing, setEditing] = useState<Faculty | null>(null)
  const [detail, setDetail] = useState<FacultyWithAvailability | null>(null)
  const [availabilityForm, setAvailabilityForm] = useState<{ day: number; slot: number; is_available: boolean }[]>([])
  const [submitAttempted, setSubmitAttempted] = useState(false)

  const load = () => {
    setLoading(true)
    facultyApi.list().then(setList).catch(() => setList([])).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitAttempted(true)
    if (!form.name.trim()) return
    facultyApi.create({ name: form.name.trim(), email: form.email.trim() || undefined })
      .then(() => { setForm({ name: '', email: '' }); load() })
      .catch((err) => alert(err.message))
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitAttempted(true)
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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Faculty Management</h1>
        <p className="mt-1 text-sm text-slate-600">Add faculty and define availability by day + slot.</p>
      </div>

      <Card>
        <CardHeader
          title={editing ? 'Edit faculty' : 'Add faculty'}
          description="Create faculty profiles used when assigning subjects and validating schedules."
          actions={
            editing ? (
              <Button
                variant="ghost"
                onClick={() => {
                  setEditing(null)
                  setForm({ name: '', email: '' })
                  setSubmitAttempted(false)
                }}
              >
                Cancel
              </Button>
            ) : null
          }
        />
        <CardContent className="p-6">
          <form onSubmit={editing ? handleUpdate : handleCreate} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Field
              label="Name"
              required
              error={submitAttempted && !form.name.trim() ? 'Name is required.' : undefined}
              className="sm:col-span-1"
            >
              <TextInput
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Dr. Smith"
                hasError={submitAttempted && !form.name.trim()}
                required
              />
            </Field>
            <Field label="Email" hint="Optional" className="sm:col-span-1">
              <TextInput
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                placeholder="smith@school.edu"
              />
            </Field>
            <div className="sm:col-span-1 flex items-end gap-2">
              <Button type="submit" className="w-full sm:w-auto">
                <Save className="h-4 w-4" />
                {editing ? 'Update' : 'Add'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Faculty list" description="Open availability to configure (day, slot) constraints." />
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6 text-sm text-slate-600">Loading…</div>
          ) : list.length === 0 ? (
            <div className="p-6 text-sm text-slate-600">No faculty yet. Add one above.</div>
          ) : (
            <Table>
              <THead>
                <tr>
                  <TH>Name</TH>
                  <TH>Email</TH>
                  <TH className="text-right">Actions</TH>
                </tr>
              </THead>
              <TBody>
                {list.map((f) => (
                  <TR key={f.id}>
                    <TD className="font-medium text-slate-900">{f.name}</TD>
                    <TD className="text-slate-600">{f.email || '—'}</TD>
                    <TD className="text-right">
                      <div className="inline-flex flex-wrap justify-end gap-2">
                        <Button variant="secondary" size="sm" onClick={() => openDetail(f.id)}>
                          Availability
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => openEdit(f)}>
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => {
                            if (confirm('Delete this faculty?')) {
                              facultyApi.delete(f.id).then(load).catch((err) => alert(err.message))
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

      <Modal
        open={Boolean(detail)}
        title={detail ? `Availability – ${detail.name}` : 'Availability'}
        description="Day: 0=Mon, 1=Tue, … Slot: 0,1,2,… Toggle availability for each slot."
        onClose={() => setDetail(null)}
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button variant="outline" onClick={() => setDetail(null)}>
              Close
            </Button>
            <Button variant="secondary" onClick={addAvailabilitySlot}>
              <Plus className="h-4 w-4" />
              Add slot
            </Button>
            <Button onClick={saveAvailability}>
              <Save className="h-4 w-4" />
              Save
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          {availabilityForm.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
              No availability slots configured yet.
            </div>
          ) : null}

          <div className="space-y-2">
            {availabilityForm.map((av, i) => (
              <div key={i} className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-3 sm:grid-cols-12 sm:items-end">
                <div className="sm:col-span-4">
                  <Field label="Day">
                    <Select value={av.day} onChange={(e) => updateAvailabilitySlot(i, 'day', Number(e.target.value))}>
                      {DAY_NAMES.map((d, idx) => (
                        <option key={d} value={idx}>
                          {d}
                        </option>
                      ))}
                    </Select>
                  </Field>
                </div>
                <div className="sm:col-span-3">
                  <Field label="Slot">
                    <NumberInput
                      min={0}
                      value={av.slot}
                      onChange={(e) => updateAvailabilitySlot(i, 'slot', Number(e.target.value))}
                    />
                  </Field>
                </div>
                <div className="sm:col-span-3">
                  <div className="space-y-1.5">
                    <div className="text-sm font-medium text-slate-800">Available</div>
                    <label className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={av.is_available}
                        onChange={(e) => updateAvailabilitySlot(i, 'is_available', e.target.checked)}
                      />
                      {av.is_available ? 'Yes' : 'No'}
                    </label>
                  </div>
                </div>
                <div className="sm:col-span-2 flex sm:justify-end">
                  <Button variant="outline" size="sm" onClick={() => removeAvailabilitySlot(i)}>
                    <Trash2 className="h-4 w-4" />
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Modal>
    </div>
  )
}
