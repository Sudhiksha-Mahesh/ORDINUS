import { useEffect, useState } from 'react'
import { Plus, Save, Trash2 } from 'lucide-react'
import { subjectApi, classApi, facultyApi, type Subject, type Class, type ClassSubject, type Faculty, type SubjectType } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, NumberInput, Select, TextInput } from '../components/ui/Form'
import { Table, TBody, TD, TH, THead, TR } from '../components/ui/Table'

export default function SubjectManagement() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState<{
    name: string
    type: SubjectType
    faculty_id: string
    lab_faculty1: string
    lab_faculty2: string
  }>({
    name: '',
    type: 'theory',
    faculty_id: '',
    lab_faculty1: '',
    lab_faculty2: '',
  })
  const [editing, setEditing] = useState<Subject | null>(null)
  const [classSubjects, setClassSubjects] = useState<ClassSubject[]>([])
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [addToClassForm, setAddToClassForm] = useState({ subject_id: '', hours_per_week: 6 })
  const [subjectSubmitAttempted, setSubjectSubmitAttempted] = useState(false)
  const [assignSubmitAttempted, setAssignSubmitAttempted] = useState(false)

  const loadSubjects = () => subjectApi.list().then(setSubjects).catch(() => setSubjects([]))
  const loadClasses = () => classApi.list().then(setClasses).catch(() => setClasses([]))
  const loadFaculties = () => facultyApi.list().then(setFaculties).catch(() => setFaculties([]))
  useEffect(() => {
    setLoading(true)
    Promise.all([loadSubjects(), loadClasses(), loadFaculties()]).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (selectedClassId != null) {
      subjectApi.listByClass(selectedClassId).then(setClassSubjects).catch(() => setClassSubjects([]))
    } else {
      setClassSubjects([])
    }
  }, [selectedClassId])

  const handleCreateSubject = (e: React.FormEvent) => {
    e.preventDefault()
    setSubjectSubmitAttempted(true)
    if (!form.name.trim()) return
    if (form.type === 'lab') {
      if (!form.lab_faculty1 || !form.lab_faculty2) {
        alert('Please select two faculty members for lab.')
        return
      }
      if (form.lab_faculty1 === form.lab_faculty2) {
        alert('Lab must be handled by two different faculty.')
        return
      }
    }
    subjectApi
      .create({
        name: form.name.trim(),
        type: form.type,
        faculty_id: form.faculty_id ? Number(form.faculty_id) : undefined,
      })
      .then(async (created) => {
        if (form.type === 'lab') {
          await subjectApi.setLabFaculty(created.id, [
            Number(form.lab_faculty1),
            Number(form.lab_faculty2),
          ])
        }
        setForm({
          name: '',
          type: 'theory',
          faculty_id: '',
          lab_faculty1: '',
          lab_faculty2: '',
        })
        loadSubjects()
      })
      .catch((err) => alert(err.message))
  }

  const handleUpdateSubject = (e: React.FormEvent) => {
    e.preventDefault()
    setSubjectSubmitAttempted(true)
    if (!editing) return
    if (form.type === 'lab') {
      if (!form.lab_faculty1 || !form.lab_faculty2) {
        alert('Please select two faculty members for lab.')
        return
      }
      if (form.lab_faculty1 === form.lab_faculty2) {
        alert('Lab must be handled by two different faculty.')
        return
      }
    }
    subjectApi
      .update(editing.id, {
        name: form.name.trim(),
        type: form.type,
        faculty_id: form.faculty_id ? Number(form.faculty_id) : undefined,
      })
      .then(async () => {
        if (form.type === 'lab') {
          await subjectApi.setLabFaculty(editing.id, [
            Number(form.lab_faculty1),
            Number(form.lab_faculty2),
          ])
        }
        setEditing(null)
        setForm({
          name: '',
          type: 'theory',
          faculty_id: '',
          lab_faculty1: '',
          lab_faculty2: '',
        })
        loadSubjects()
      })
      .catch((err) => alert(err.message))
  }

  const openEditSubject = (s: Subject) => {
    setEditing(s)
    setForm({
      name: s.name,
      type: (s.type as SubjectType) ?? 'theory',
      faculty_id: s.faculty_id != null ? String(s.faculty_id) : '',
      lab_faculty1: '',
      lab_faculty2: '',
    })
  }

  const handleAddToClass = (e: React.FormEvent) => {
    e.preventDefault()
    setAssignSubmitAttempted(true)
    if (selectedClassId == null || !addToClassForm.subject_id) return
    subjectApi.addToClass(selectedClassId, {
      subject_id: Number(addToClassForm.subject_id),
      hours_per_week: Number(addToClassForm.hours_per_week) || 1,
    })
      .then(() => {
        setAddToClassForm({ subject_id: '', hours_per_week: 6 })
        subjectApi.listByClass(selectedClassId).then(setClassSubjects)
      })
      .catch((err) => alert(err.message))
  }

  const removeFromClass = (subjectId: number) => {
    if (selectedClassId == null) return
    subjectApi.removeFromClass(selectedClassId, subjectId).then(() =>
      subjectApi.listByClass(selectedClassId).then(setClassSubjects)
    ).catch((err) => alert(err.message))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Subject Management</h1>
        <p className="mt-1 text-sm text-slate-600">Create subjects, optionally map them to faculty, then assign hours/week per class.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <Card>
            <CardHeader
              title={editing ? 'Edit subject' : 'Add subject'}
              description="Subjects can later be assigned to classes with hours/week."
              actions={
                editing ? (
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setEditing(null)
                      setForm({
                        name: '',
                        type: 'theory',
                        faculty_id: '',
                        lab_faculty1: '',
                        lab_faculty2: '',
                      })
                      setSubjectSubmitAttempted(false)
                    }}
                  >
                    Cancel
                  </Button>
                ) : null
              }
            />
            <CardContent className="p-6">
              <form onSubmit={editing ? handleUpdateSubject : handleCreateSubject} className="space-y-4">
                <Field
                  label="Name"
                  required
                  error={subjectSubmitAttempted && !form.name.trim() ? 'Subject name is required.' : undefined}
                >
                  <TextInput
                    value={form.name}
                    onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    placeholder="Mathematics"
                    hasError={subjectSubmitAttempted && !form.name.trim()}
                    required
                  />
                </Field>
                <Field label="Faculty" hint="Optional">
                  <Select value={form.faculty_id} onChange={(e) => setForm((f) => ({ ...f, faculty_id: e.target.value }))}>
                    <option value="">— None —</option>
                    {faculties.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name}
                      </option>
                    ))}
                  </Select>
                </Field>
                <Field label="Type" required hint="Theory: 3h/week · Lab: 2×2 consecutive">
                  <Select
                    value={form.type}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, type: (e.target.value as SubjectType) || 'theory' }))
                    }
                  >
                    <option value="theory">Theory</option>
                    <option value="lab">Lab</option>
                  </Select>
                </Field>
                {form.type === 'lab' && (
                  <Field
                    label="Lab faculty (2)"
                    required
                    hint="Select two different staff for lab sessions."
                  >
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      <Select
                        value={form.lab_faculty1}
                        onChange={(e) =>
                          setForm((f) => ({ ...f, lab_faculty1: e.target.value }))
                        }
                      >
                        <option value="">— Select staff 1 —</option>
                        {faculties.map((f) => (
                          <option key={f.id} value={f.id}>
                            {f.name}
                          </option>
                        ))}
                      </Select>
                      <Select
                        value={form.lab_faculty2}
                        onChange={(e) =>
                          setForm((f) => ({ ...f, lab_faculty2: e.target.value }))
                        }
                      >
                        <option value="">— Select staff 2 —</option>
                        {faculties.map((f) => (
                          <option key={f.id} value={f.id}>
                            {f.name}
                          </option>
                        ))}
                      </Select>
                    </div>
                  </Field>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button type="submit">
                    <Save className="h-4 w-4" />
                    {editing ? 'Update' : 'Add'}
                  </Button>
                </div>
              </form>
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
                Tip: Define faculty availability on the Faculty page to improve generation quality.
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Subjects" description="Manage your subject catalog and faculty mappings." />
            <CardContent className="p-0">
              {loading ? (
                <div className="p-6 text-sm text-slate-600">Loading…</div>
              ) : subjects.length === 0 ? (
                <div className="p-6 text-sm text-slate-600">No subjects yet.</div>
              ) : (
                <Table>
                  <THead>
                    <tr>
                      <TH>Subject</TH>
                      <TH>Type</TH>
                      <TH>Faculty</TH>
                      <TH className="text-right">Actions</TH>
                    </tr>
                  </THead>
                  <TBody>
                    {subjects.map((s) => (
                      <TR key={s.id}>
                        <TD className="font-medium text-slate-900">{s.name}</TD>
                        <TD className="text-xs font-medium uppercase tracking-wide text-slate-600">
                          {(s.type ?? 'theory') === 'lab' ? 'LAB' : 'THEORY'}
                        </TD>
                        <TD className="text-slate-600">{s.faculty_name || '—'}</TD>
                        <TD className="text-right">
                          <div className="inline-flex flex-wrap justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={() => openEditSubject(s)}>
                              Edit
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => {
                                if (confirm('Delete?')) subjectApi.delete(s.id).then(loadSubjects)
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

        <div className="space-y-6">
          <Card>
            <CardHeader title="Assign to class" description="Set hours/week for each subject within a specific class." />
            <CardContent className="p-6 space-y-4">
              <Field label="Class">
                <Select
                  value={selectedClassId ?? ''}
                  onChange={(e) => {
                    setSelectedClassId(e.target.value ? Number(e.target.value) : null)
                    setAssignSubmitAttempted(false)
                  }}
                >
                  <option value="">— Select class —</option>
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </Select>
              </Field>

              {selectedClassId != null ? (
                <>
                  <form onSubmit={handleAddToClass} className="grid grid-cols-1 gap-4 md:grid-cols-3 md:items-end">
                    <Field
                      label="Subject"
                      required
                      error={assignSubmitAttempted && !addToClassForm.subject_id ? 'Select a subject.' : undefined}
                      className="md:col-span-2"
                    >
                      <Select
                        value={addToClassForm.subject_id}
                        onChange={(e) => setAddToClassForm((f) => ({ ...f, subject_id: e.target.value }))}
                        hasError={assignSubmitAttempted && !addToClassForm.subject_id}
                        required
                      >
                        <option value="">— Select —</option>
                        {subjects.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name}
                          </option>
                        ))}
                      </Select>
                    </Field>
                    <Field label="Hours/week" hint="1–20" className="md:col-span-1">
                      <NumberInput
                        min={1}
                        max={20}
                        value={addToClassForm.hours_per_week}
                        onChange={(e) => setAddToClassForm((f) => ({ ...f, hours_per_week: Number(e.target.value) }))}
                      />
                    </Field>
                    <div className="md:col-span-3">
                      <Button type="submit" variant="secondary">
                        <Plus className="h-4 w-4" />
                        Add to class
                      </Button>
                    </div>
                  </form>

                  <div className="pt-2">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-semibold text-slate-900">Subjects in this class</div>
                      <div className="text-xs text-slate-500">{classSubjects.length} item(s)</div>
                    </div>
                    <div className="mt-3 rounded-xl border border-slate-200 overflow-hidden bg-white">
                      {classSubjects.length === 0 ? (
                        <div className="p-4 text-sm text-slate-600">None yet.</div>
                      ) : (
                        <Table>
                          <THead>
                            <tr>
                              <TH>Subject</TH>
                              <TH>Hours/week</TH>
                              <TH className="text-right">Actions</TH>
                            </tr>
                          </THead>
                          <TBody>
                            {classSubjects.map((cs) => (
                              <TR key={cs.id}>
                                <TD className="font-medium text-slate-900">{cs.subject_name || `#${cs.subject_id}`}</TD>
                                <TD>{cs.hours_per_week}</TD>
                                <TD className="text-right">
                                  <Button variant="outline" size="sm" onClick={() => removeFromClass(cs.subject_id)}>
                                    <Trash2 className="h-4 w-4" />
                                    Remove
                                  </Button>
                                </TD>
                              </TR>
                            ))}
                          </TBody>
                        </Table>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
                  Select a class to assign subjects and hours/week.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
