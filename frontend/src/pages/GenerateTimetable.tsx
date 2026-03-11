import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Sparkles, Wand2 } from 'lucide-react'
import { classApi, timetableApi, type Class } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Select } from '../components/ui/Form'

export default function GenerateTimetable() {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [loadingStandard, setLoadingStandard] = useState(false)
  const [loadingGA, setLoadingGA] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    classApi.list().then(setClasses).catch(() => setClasses([]))
  }, [])

  const handleGenerateStandard = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedClassId == null) return
    setLoadingStandard(true)
    setMessage(null)
    timetableApi.generate(selectedClassId)
      .then((res) => {
        setMessage(res.message)
        navigate(`/timetable/${selectedClassId}`)
      })
      .catch((err) => {
        setMessage(err.message || 'Generation failed.')
      })
      .finally(() => setLoadingStandard(false))
  }

  const handleGenerateGA = () => {
    if (selectedClassId == null) return
    setLoadingGA(true)
    setMessage(null)
    timetableApi
      .generateGA({
        class_id: selectedClassId,
        population_size: 80,
        generations: 300,
        seed: 42,
      })
      .then(() => {
        setMessage('Generated using Genetic Algorithm.')
        navigate(`/timetable/${selectedClassId}`)
      })
      .catch((err) => {
        setMessage(err.message || 'GA generation failed.')
      })
      .finally(() => setLoadingGA(false))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Generate Timetable</h1>
        <p className="mt-1 text-sm text-slate-600">
          Select a class and run the scheduler. Use Genetic Algorithm generation to enforce subject-type rules (theory/lab blocks) more strictly.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader
          title="Generation"
          description="Choose a generator. Both options open the same timetable view once complete."
        />
        <CardContent className="p-6 space-y-4">
          <form onSubmit={handleGenerateStandard} className="space-y-4">
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

            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <Button type="submit" disabled={loadingStandard || loadingGA || selectedClassId == null}>
                <Wand2 className="h-4 w-4" />
                {loadingStandard ? 'Generating…' : 'Generate (Standard)'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={handleGenerateGA}
                disabled={loadingStandard || loadingGA || selectedClassId == null}
              >
                <Sparkles className="h-4 w-4" />
                {loadingGA ? 'Generating…' : 'Generate (GA)'}
              </Button>
              {selectedClassId != null ? (
                <Button variant="outline" type="button" onClick={() => navigate(`/timetable/${selectedClassId}`)}>
                  View current timetable
                  <ArrowRight className="h-4 w-4" />
                </Button>
              ) : null}
            </div>
            <div className="text-xs text-slate-600">
              GA defaults: population 80 · generations 300 · seed 42
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
