import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { classApi, timetableApi, type Class } from '../services/api'

export default function GenerateTimetable() {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    classApi.list().then(setClasses).catch(() => setClasses([]))
  }, [])

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedClassId == null) return
    setLoading(true)
    setMessage(null)
    timetableApi.generate(selectedClassId)
      .then((res) => {
        setMessage(res.message)
        navigate(`/timetable/${selectedClassId}`)
      })
      .catch((err) => {
        setMessage(err.message || 'Generation failed.')
      })
      .finally(() => setLoading(false))
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800 mb-2">Generate Timetable</h1>
      <p className="text-slate-600 mb-6">
        Select a class and run the backtracking scheduler. Ensure faculty, subjects, and faculty availability are configured.
      </p>

      <form onSubmit={handleGenerate} className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm max-w-md">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Class</label>
          <select
            value={selectedClassId ?? ''}
            onChange={(e) => setSelectedClassId(e.target.value ? Number(e.target.value) : null)}
            className="border border-slate-300 rounded px-3 py-2 w-full"
            required
          >
            <option value="">— Select class —</option>
            {classes.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        {message && (
          <p className={`mb-4 text-sm ${message.startsWith('Generated') ? 'text-green-700' : 'text-red-600'}`}>
            {message}
          </p>
        )}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading || selectedClassId == null}
            className="px-4 py-2 bg-primary-700 text-white rounded font-medium hover:bg-primary-800 disabled:opacity-50"
          >
            {loading ? 'Generating…' : 'Generate'}
          </button>
          {selectedClassId != null && (
            <button
              type="button"
              onClick={() => navigate(`/timetable/${selectedClassId}`)}
              className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50"
            >
              View current timetable
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
