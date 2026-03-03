import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { classApi, facultyApi, subjectApi } from '../services/api'

export default function Dashboard() {
  const [counts, setCounts] = useState({ faculty: 0, classes: 0, subjects: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([facultyApi.list(), classApi.list(), subjectApi.list()])
      .then(([f, c, s]) => setCounts({ faculty: f.length, classes: c.length, subjects: s.length }))
      .catch(() => setCounts({ faculty: 0, classes: 0, subjects: 0 }))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800 mb-2">Dashboard</h1>
      <p className="text-slate-600 mb-8">
        Configure faculty, classes, and subjects, then generate timetables.
      </p>
      {loading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Link
            to="/faculty"
            className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:shadow transition-shadow"
          >
            <h2 className="font-medium text-primary-800">Faculty</h2>
            <p className="text-2xl font-semibold text-slate-700 mt-1">{counts.faculty}</p>
            <p className="text-sm text-slate-500 mt-1">Manage faculty & availability</p>
          </Link>
          <Link
            to="/classes"
            className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:shadow transition-shadow"
          >
            <h2 className="font-medium text-primary-800">Classes</h2>
            <p className="text-2xl font-semibold text-slate-700 mt-1">{counts.classes}</p>
            <p className="text-sm text-slate-500 mt-1">Working days & slots</p>
          </Link>
          <Link
            to="/subjects"
            className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:shadow transition-shadow"
          >
            <h2 className="font-medium text-primary-800">Subjects</h2>
            <p className="text-2xl font-semibold text-slate-700 mt-1">{counts.subjects}</p>
            <p className="text-sm text-slate-500 mt-1">Assign faculty & hours</p>
          </Link>
        </div>
      )}
      <div className="mt-10">
        <Link
          to="/generate"
          className="inline-flex items-center px-4 py-2 bg-primary-700 text-white rounded-lg font-medium hover:bg-primary-800 transition-colors"
        >
          Generate Timetable
        </Link>
      </div>
    </div>
  )
}
