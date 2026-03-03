import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { timetableApi, type TimetableGrid } from '../services/api'

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function ViewTimetable() {
  const { classId } = useParams<{ classId: string }>()
  const [data, setData] = useState<TimetableGrid | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-slate-800">Timetable – {data.class_name}</h1>
        <Link to="/generate" className="text-primary-700 font-medium hover:underline">Generate / Back</Link>
      </div>
      <p className="text-slate-600 mb-4">
        Rows = days, Columns = slots. Each cell shows subject and faculty.
      </p>
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-x-auto">
        <table className="w-full border-collapse min-w-[600px]">
          <thead>
            <tr className="bg-slate-100">
              <th className="border border-slate-200 p-2 text-left font-medium text-slate-700 w-28">Day</th>
              {Array.from({ length: data.slots_per_day }, (_, i) => (
                <th key={i} className="border border-slate-200 p-2 text-center font-medium text-slate-700">
                  Slot {i + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.grid.map((row, dayIndex) => (
              <tr key={dayIndex} className="hover:bg-slate-50">
                <td className="border border-slate-200 p-2 font-medium text-slate-700">
                  {DAY_NAMES[dayIndex] ?? `Day ${dayIndex + 1}`}
                </td>
                {row.map((cell, slotIndex) => (
                  <td key={slotIndex} className="border border-slate-200 p-3 align-top">
                    {cell ? (
                      <div className="text-sm">
                        <div className="font-medium text-slate-800">{cell.subject_name}</div>
                        <div className="text-slate-600">{cell.faculty_name}</div>
                      </div>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
