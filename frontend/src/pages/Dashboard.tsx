import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, GraduationCap, Users, Wand2 } from 'lucide-react'
import { classApi, facultyApi, subjectApi } from '../services/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

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
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">
            Configure faculty, classes, and subjects, then generate conflict-aware timetables.
          </p>
        </div>
        <Link to="/generate" className="inline-flex">
          <Button>
            <Wand2 className="h-4 w-4" />
            Generate timetable
          </Button>
        </Link>
      </div>
      {loading ? (
        <Card>
          <CardContent className="p-6 text-slate-600">Loading overview…</CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Link to="/faculty" className="group">
            <Card className="transition hover:shadow-md">
              <CardHeader
                title={
                  <span className="inline-flex items-center gap-2">
                    <span className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-100">
                      <Users className="h-4 w-4" />
                    </span>
                    Faculty
                  </span>
                }
                description="Manage staff & availability"
                actions={<ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600" />}
              />
              <CardContent className="p-6">
                <div className="text-3xl font-semibold tracking-tight text-slate-900">{counts.faculty}</div>
                <div className="mt-1 text-sm text-slate-600">active faculty records</div>
              </CardContent>
            </Card>
          </Link>

          <Link to="/classes" className="group">
            <Card className="transition hover:shadow-md">
              <CardHeader
                title={
                  <span className="inline-flex items-center gap-2">
                    <span className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-100">
                      <GraduationCap className="h-4 w-4" />
                    </span>
                    Classes
                  </span>
                }
                description="Working days & slots"
                actions={<ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600" />}
              />
              <CardContent className="p-6">
                <div className="text-3xl font-semibold tracking-tight text-slate-900">{counts.classes}</div>
                <div className="mt-1 text-sm text-slate-600">configured cohorts</div>
              </CardContent>
            </Card>
          </Link>

          <Link to="/subjects" className="group">
            <Card className="transition hover:shadow-md">
              <CardHeader
                title={
                  <span className="inline-flex items-center gap-2">
                    <span className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-100">
                      <BookOpen className="h-4 w-4" />
                    </span>
                    Subjects
                  </span>
                }
                description="Assign faculty & hours/week"
                actions={<ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600" />}
              />
              <CardContent className="p-6">
                <div className="text-3xl font-semibold tracking-tight text-slate-900">{counts.subjects}</div>
                <div className="mt-1 text-sm text-slate-600">subjects in catalog</div>
              </CardContent>
            </Card>
          </Link>
        </div>
      )}
    </div>
  )
}
