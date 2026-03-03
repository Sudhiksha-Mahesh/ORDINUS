import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/faculty', label: 'Faculty' },
  { path: '/classes', label: 'Classes' },
  { path: '/subjects', label: 'Subjects' },
  { path: '/generate', label: 'Generate Timetable' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-xl font-semibold text-primary-800 tracking-tight">
              Ordinus
            </Link>
            <p className="text-sm text-slate-500">Academic Timetable Generator</p>
          </div>
          <nav className="mt-4 flex gap-1 flex-wrap">
            {navItems.map(({ path, label }) => (
              <Link
                key={path}
                to={path}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'bg-primary-100 text-primary-800'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-sm text-slate-500">
        Ordinus &copy; {new Date().getFullYear()} – Foundational version
      </footer>
    </div>
  )
}
