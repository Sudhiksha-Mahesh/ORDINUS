import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, Info } from 'lucide-react'
import { timetableApi, type TimetableGrid } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { cn } from '../utils/cn'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function ViewTimetable() {
  const { classId } = useParams<{ classId: string }>()
  const [data, setData] = useState<TimetableGrid | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const repeatedFacultyByDay = useMemo(() => {
    const grid = data?.grid ?? []
    const map = new Map<number, Set<string>>()
    grid.forEach((row, dayIndex) => {
      const counts = new Map<string, number>()
      row.forEach((cell) => {
        if (!cell?.faculty_name) return
        counts.set(cell.faculty_name, (counts.get(cell.faculty_name) || 0) + 1)
      })
      const repeated = new Set<string>()
      counts.forEach((count, name) => {
        if (count > 1) repeated.add(name)
      })
      map.set(dayIndex, repeated)
    })
    return map
  }, [data?.grid])

  useEffect(() => {
    if (!classId) return
    setLoading(true)
    setError(null)
    timetableApi.get(Number(classId))
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load timetable'))
      .finally(() => setLoading(false))
  }, [classId])

  if (!classId) {
    return (
      <div>
        <p className="text-slate-600">Invalid class.</p>
        <Link to="/generate" className="text-primary-700 font-medium hover:underline">Back to Generate</Link>
      </div>
    )
  }

  if (loading) return <p className="text-slate-600">Loading timetable…</p>
  if (error) {
    return (
      <div>
        <p className="text-red-600">{error}</p>
        <Link to="/generate" className="text-primary-700 font-medium hover:underline mt-2 inline-block">Back to Generate</Link>
      </div>
    )
  }
  if (!data) return null

  const breakAfterSlots = data.break_after_slots ?? []
  type Col = { type: 'slot'; index: number } | { type: 'break' }
  const columns: Col[] = []
  for (let s = 0; s < data.slots_per_day; s++) {
    columns.push({ type: 'slot', index: s })
    if (breakAfterSlots.includes(s + 1)) columns.push({ type: 'break' })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Timetable</h1>
          <p className="mt-1 text-sm text-slate-600">
            Class: <span className="font-semibold text-slate-900">{data.class_name}</span> · Days: {data.working_days} · Slots/day: {data.slots_per_day}
          </p>
        </div>
        <Link to="/generate" className="inline-flex">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4" />
            Back to Generate
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader
          title="Schedule grid"
          description={
            <span className="inline-flex flex-wrap items-center gap-x-4 gap-y-2">
              <span className="inline-flex items-center gap-2">
                <span className="h-3 w-3 rounded bg-slate-100 ring-1 ring-inset ring-slate-200" />
                <span>Empty slot</span>
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-3 w-3 rounded bg-amber-100 ring-1 ring-inset ring-amber-200" />
                <span>Repeated faculty (review)</span>
              </span>
              <span className="inline-flex items-center gap-2 text-slate-500">
                <Info className="h-4 w-4" />
                Hover cells for clarity
              </span>
            </span>
          }
          actions={
            <div className="hidden sm:flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600 ring-1 ring-inset ring-slate-200">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              Conflict highlighting depends on backend data; repeated faculty is a heuristic.
            </div>
          }
        />
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-[760px] w-full border-separate border-spacing-0 text-sm">
              <thead className="sticky top-0 z-10">
                <tr>
                  <th className="sticky left-0 z-20 bg-white border-b border-slate-200 px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 w-40">
                    Day
                  </th>
                  {columns.map((col, i) =>
                    col.type === 'slot' ? (
                      <th
                        key={`s-${col.index}`}
                        className="bg-white border-b border-slate-200 px-4 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-600"
                      >
                        Slot {col.index + 1}
                      </th>
                    ) : (
                      <th
                        key={`b-${i}`}
                        className="bg-slate-100 border-b border-slate-200 px-2 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-600 w-20"
                      >
                        Break
                      </th>
                    )
                  )}
                </tr>
              </thead>
              <tbody>
                {data.grid.map((row, dayIndex) => (
                  <tr key={dayIndex} className="group">
                    <td className="sticky left-0 z-10 bg-white border-b border-slate-200 px-4 py-3 font-semibold text-slate-900">
                      {DAY_NAMES[dayIndex] ?? `Day ${dayIndex + 1}`}
                    </td>
                    {columns.map((col, colKey) => {
                      if (col.type === 'break') {
                        return (
                          <td
                            key={`b-${colKey}`}
                            className="border-b border-slate-200 px-2 py-3 align-middle bg-slate-100/80"
                          >
                            <div className="text-center text-xs font-medium text-slate-600">Break</div>
                          </td>
                        )
                      }
                      const cell = row[col.index]
                      const repeatedSet = repeatedFacultyByDay.get(dayIndex) || new Set<string>()
                      const isRepeatedFaculty = Boolean(cell?.faculty_name && repeatedSet.has(cell.faculty_name))
                      const isEmpty = !cell
                      const normalizedType =
                        cell?.slot_type === 'lab' || cell?.slot_type === 'extra' || cell?.slot_type === 'theory'
                          ? cell.slot_type
                          : cell?.faculty_name?.includes(',')
                            ? 'lab'
                            : 'theory'
                      const slotColorClass =
                        normalizedType === 'lab'
                          ? 'bg-emerald-50/90 ring-emerald-200'
                          : 'bg-orange-50/90 ring-orange-200'
                      return (
                        <td
                          key={`s-${col.index}`}
                          className={cn(
                            'border-b border-slate-200 px-3 py-3 align-top transition',
                            'group-hover:bg-slate-50/50',
                            isEmpty ? 'bg-slate-50' : 'bg-white',
                          )}
                        >
                          <div
                            className={cn(
                              'h-full rounded-xl p-3 ring-1 ring-inset transition',
                              isEmpty
                                ? 'bg-slate-100/40 ring-slate-200 border border-dashed border-slate-200'
                                : isRepeatedFaculty
                                  ? 'bg-amber-50 ring-amber-200'
                                  : `${slotColorClass} hover:ring-indigo-200`,
                            )}
                            title={
                              cell
                                ? `${cell.subject_name} — ${cell.faculty_name}`
                                : 'Empty slot'
                            }
                          >
                            {cell ? (
                              <div className="space-y-1">
                                <div className="font-semibold text-slate-900 leading-snug">{cell.subject_name}</div>
                                <div className={cn('text-xs leading-snug', isRepeatedFaculty ? 'text-amber-900' : 'text-slate-600')}>
                                  {cell.faculty_name}
                                </div>
                              </div>
                            ) : (
                              <div className="text-xs font-medium text-slate-500">Empty</div>
                            )}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
