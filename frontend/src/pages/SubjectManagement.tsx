import { useEffect, useState } from 'react'
import { subjectApi, classApi, facultyApi, type Subject, type Class, type ClassSubject, type Faculty } from '../services/api'

export default function SubjectManagement() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', faculty_id: '' })
  const [editing, setEditing] = useState<Subject | null>(null)
  const [classSubjects, setClassSubjects] = useState<ClassSubject[]>([])
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [addToClassForm, setAddToClassForm] = useState({ subject_id: '', hours_per_week: 6 })

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
    if (!form.name.trim()) return
    subjectApi.create({ name: form.name.trim(), faculty_id: form.faculty_id ? Number(form.faculty_id) : undefined })
      .then(() => { setForm({ name: '', faculty_id: '' }); loadSubjects() })
      .catch((err) => alert(err.message))
  }

  const handleUpdateSubject = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editing) return
    subjectApi.update(editing.id, { name: form.name.trim(), faculty_id: form.faculty_id ? Number(form.faculty_id) : undefined })
      .then(() => { setEditing(null); setForm({ name: '', faculty_id: '' }); loadSubjects() })
      .catch((err) => alert(err.message))
  }

  const openEditSubject = (s: Subject) => {
    setEditing(s)
    setForm({ name: s.name, faculty_id: s.faculty_id != null ? String(s.faculty_id) : '' })
  }

  const handleAddToClass = (e: React.FormEvent) => {
    e.preventDefault()
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
    <div>
      <h1 className="text-2xl font-semibold text-slate-800 mb-2">Subject Management</h1>
      <p className="text-slate-600 mb-6">Add subjects, assign faculty, and set hours per week per class.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div className="bg-white border border-slate-200 rounded-lg p-4 mb-4 shadow-sm">
            <h2 className="font-medium text-slate-700 mb-3">{editing ? 'Edit subject' : 'Add subject'}</h2>
            <form onSubmit={editing ? handleUpdateSubject : handleCreateSubject} className="space-y-3">
              <div>
                <label className="block text-sm text-slate-600 mb-1">Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  className="border border-slate-300 rounded px-3 py-2 w-full"
                  placeholder="Mathematics"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-slate-600 mb-1">Faculty (optional)</label>
                <select
                  value={form.faculty_id}
                  onChange={(e) => setForm((f) => ({ ...f, faculty_id: e.target.value }))}
                  className="border border-slate-300 rounded px-3 py-2 w-full"
                >
                  <option value="">— None —</option>
                  {faculties.map((f) => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button type="submit" className="px-4 py-2 bg-primary-700 text-white rounded font-medium">
                  {editing ? 'Update' : 'Add'}
                </button>
                {editing && (
                  <button type="button" onClick={() => { setEditing(null); setForm({ name: '', faculty_id: '' }); }} className="px-4 py-2 border rounded">
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>
          <p className="text-sm text-slate-500 mb-2">Assign faculty from Faculty page; then select here when adding/editing a subject.</p>
          <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
            <h2 className="font-medium text-slate-700 p-4 border-b border-slate-200">Subjects</h2>
            {loading ? (
              <p className="p-4 text-slate-500">Loading…</p>
            ) : subjects.length === 0 ? (
              <p className="p-4 text-slate-500">No subjects yet.</p>
            ) : (
              <ul className="divide-y divide-slate-100">
                {subjects.map((s) => (
                  <li key={s.id} className="p-4 flex justify-between items-center">
                    <span>{s.name} {s.faculty_name ? `(${s.faculty_name})` : ''}</span>
                    <span>
                      <button type="button" onClick={() => openEditSubject(s)} className="text-primary-700 font-medium hover:underline mr-2">Edit</button>
                      <button type="button" onClick={() => { if (confirm('Delete?')) subjectApi.delete(s.id).then(loadSubjects); }} className="text-red-600 hover:underline">Delete</button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div>
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
            <h2 className="font-medium text-slate-700 mb-3">Assign subject to class (hours per week)</h2>
            <div className="mb-3">
              <label className="block text-sm text-slate-600 mb-1">Class</label>
              <select
                value={selectedClassId ?? ''}
                onChange={(e) => setSelectedClassId(e.target.value ? Number(e.target.value) : null)}
                className="border border-slate-300 rounded px-3 py-2 w-full"
              >
                <option value="">— Select class —</option>
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            {selectedClassId != null && (
              <>
                <form onSubmit={handleAddToClass} className="flex flex-wrap gap-3 items-end">
                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Subject</label>
                    <select
                      value={addToClassForm.subject_id}
                      onChange={(e) => setAddToClassForm((f) => ({ ...f, subject_id: e.target.value }))}
                      className="border border-slate-300 rounded px-3 py-2 min-w-[140px]"
                      required
                    >
                      <option value="">— Select —</option>
                      {subjects.map((s) => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Hours/week</label>
                    <input
                      type="number"
                      min={1}
                      max={20}
                      value={addToClassForm.hours_per_week}
                      onChange={(e) => setAddToClassForm((f) => ({ ...f, hours_per_week: Number(e.target.value) }))}
                      className="border border-slate-300 rounded px-3 py-2 w-20"
                    />
                  </div>
                  <button type="submit" className="px-4 py-2 bg-primary-700 text-white rounded font-medium">Add to class</button>
                </form>
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-slate-700 mb-2">Subjects in this class</h3>
                  {classSubjects.length === 0 ? (
                    <p className="text-slate-500 text-sm">None yet.</p>
                  ) : (
                    <ul className="space-y-1">
                      {classSubjects.map((cs) => (
                        <li key={cs.id} className="flex justify-between text-sm">
                          <span>{cs.subject_name} – {cs.hours_per_week} h/wk</span>
                          <button type="button" onClick={() => removeFromClass(cs.subject_id)} className="text-red-600 hover:underline">Remove</button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
