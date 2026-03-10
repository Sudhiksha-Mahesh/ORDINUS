import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Wand2 } from 'lucide-react'
import { classApi, timetableApi, type Class } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Select } from '../components/ui/Form'

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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Generate Timetable</h1>
        <p className="mt-1 text-sm text-slate-600">
          Select a class and run the scheduler. Make sure faculty, subjects, class subjects (hours/week), and availability are configured.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader
          title="Generation"
          description="This triggers the backend generator and then opens the timetable view."
        />
        <CardContent className="p-6 space-y-4">
          <form onSubmit={handleGenerate} className="space-y-4">
            <Field label="Class" required>
              <Select
                value={selectedClassId ?? ''}
                onChange={(e) => setSelectedClassId(e.target.value ? Number(e.target.value) : null)}
                required
              >
                <option value="">— Select class —</option>
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
            </Field>

            {message ? (
              <div
                className={[
                  'rounded-xl border p-3 text-sm',
                  message.startsWith('Generated')
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
                    : 'border-rose-200 bg-rose-50 text-rose-900',
                ].join(' ')}
              >
                {message}
              </div>
            ) : null}

            <div className="flex flex-col gap-2 sm:flex-row">
              <Button type="submit" disabled={loading || selectedClassId == null}>
                <Wand2 className="h-4 w-4" />
                {loading ? 'Generating…' : 'Generate'}
              </Button>
              {selectedClassId != null ? (
                <Button variant="outline" type="button" onClick={() => navigate(`/timetable/${selectedClassId}`)}>
                  View current timetable
                  <ArrowRight className="h-4 w-4" />
                </Button>
              ) : null}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
