import { ReactNode, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BookOpen,
  GraduationCap,
  LayoutDashboard,
  Menu,
  Users,
  Wand2,
  X,
  UserCircle2,
} from 'lucide-react'
import { cn } from '../utils/cn'

type NavItem = { path: string; label: string; icon: ReactNode }

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  const navItems: NavItem[] = useMemo(
    () => [
      { path: '/', label: 'Dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
      { path: '/faculty', label: 'Faculty Management', icon: <Users className="h-4 w-4" /> },
      { path: '/classes', label: 'Classes', icon: <GraduationCap className="h-4 w-4" /> },
      { path: '/subjects', label: 'Subjects', icon: <BookOpen className="h-4 w-4" /> },
      { path: '/generate', label: 'Generate Timetable', icon: <Wand2 className="h-4 w-4" /> },
    ],
    [],
  )

  const [sidebarOpen, setSidebarOpen] = useState(false)

  const isActive = (path: string) =>
    location.pathname === path || (path !== '/' && location.pathname.startsWith(path))

  const SidebarInner = ({ onNavigate }: { onNavigate?: () => void }) => (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-3 px-4 py-4">
        <Link to="/" className="group flex items-center gap-3" onClick={onNavigate}>
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-600 text-white shadow-sm">
            <LayoutDashboard className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-900 leading-tight">Ordinus</div>
            <div className="text-xs text-slate-500 leading-tight">Academic administration</div>
          </div>
        </Link>
        <button
          type="button"
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="mt-4 flex-1 px-2">
        <div className="px-2 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Navigation
        </div>
        <div className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={onNavigate}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition',
                isActive(item.path)
                  ? 'bg-indigo-50 text-indigo-900 ring-1 ring-inset ring-indigo-100'
                  : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900',
              )}
            >
              <span
                className={cn(
                  'grid h-8 w-8 place-items-center rounded-lg',
                  isActive(item.path) ? 'bg-white text-indigo-700 shadow-sm' : 'bg-slate-100 text-slate-700',
                )}
              >
                {item.icon}
              </span>
              <span className="truncate">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3">
          <UserCircle2 className="h-9 w-9 text-slate-600" />
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-900 leading-tight truncate">Admin</div>
            <div className="text-xs text-slate-500 leading-tight truncate">Academic Office</div>
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-500">
          Ordinus &copy; {new Date().getFullYear()}
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:z-40 lg:flex lg:w-72 lg:flex-col border-r border-slate-200 bg-white">
        <SidebarInner />
      </aside>

      {/* Mobile sidebar drawer */}
      {sidebarOpen ? (
        <div className="lg:hidden">
          <div className="fixed inset-0 z-40 bg-slate-900/40" onClick={() => setSidebarOpen(false)} />
          <aside className="fixed inset-y-0 left-0 z-50 w-[18rem] border-r border-slate-200 bg-white shadow-2xl">
            <SidebarInner onNavigate={() => setSidebarOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/85 backdrop-blur">
          <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="lg:hidden rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  onClick={() => setSidebarOpen(true)}
                  aria-label="Open sidebar"
                >
                  <Menu className="h-5 w-5" />
                </button>
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-slate-900 leading-tight">Ordinus</div>
                  <div className="text-xs text-slate-500 leading-tight">Intelligent Academic Timetable Generator</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <div className="text-sm font-semibold text-slate-900 leading-tight">Admin</div>
                  <div className="text-xs text-slate-500 leading-tight">System user</div>
                </div>
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-slate-100 text-slate-700">
                  <UserCircle2 className="h-6 w-6" />
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
          {children}
        </main>
      </div>
    </div>
  )
}
