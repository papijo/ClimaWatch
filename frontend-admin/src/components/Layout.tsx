import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom'
import {
  LayoutGrid,
  Users,
  Activity,
  ClipboardList,
  Timer,
  DatabaseZap,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Bell,
} from 'lucide-react'
import { clearToken } from '../lib/auth'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutGrid },
  { to: '/contacts', label: 'Contacts', icon: Users },
  { to: '/logs', label: 'Risk Logs', icon: Activity },
  { to: '/assessments', label: 'Assessments', icon: ClipboardList },
  { to: '/pipeline', label: 'Pipeline', icon: DatabaseZap },
  { to: '/scheduler', label: 'Scheduler', icon: Timer },
]

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/contacts': 'Contacts',
  '/logs': 'Risk Logs',
  '/assessments': 'Assessments',
  '/pipeline': 'Pipeline',
  '/scheduler': 'Scheduler',
}

interface NavItemProps {
  item: (typeof NAV)[0]
  collapsed: boolean
  isActive: boolean
}

function NavItem({ item, collapsed, isActive }: NavItemProps) {
  const Icon = item.icon
  return (
    <div className="relative group/navitem">
      <Link
        to={item.to}
        className={[
          'flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-150',
          isActive
            ? 'bg-white/10 text-white'
            : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-100',
          collapsed ? 'justify-center' : '',
        ].join(' ')}
      >
        <Icon
          size={18}
          className={`shrink-0 ${isActive ? 'text-emerald-400' : ''}`}
        />
        {!collapsed && (
          <>
            <span className="text-sm font-medium leading-none truncate">{item.label}</span>
            {isActive && (
              <div className="ml-auto w-1 h-4 rounded-full bg-emerald-400 shrink-0" />
            )}
          </>
        )}
      </Link>

      {/* Tooltip — visible only when collapsed */}
      {collapsed && (
        <div className="pointer-events-none absolute left-full top-1/2 z-50 ml-2 -translate-y-1/2 rounded-md border border-zinc-700 bg-zinc-800 px-2.5 py-1.5 text-xs font-medium text-white whitespace-nowrap shadow-xl opacity-0 transition-opacity duration-100 group-hover/navitem:opacity-100">
          {item.label}
        </div>
      )}
    </div>
  )
}

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebar-collapsed') === 'true'
    } catch {
      return false
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem('sidebar-collapsed', String(collapsed))
    } catch {
      // no-op
    }
  }, [collapsed])

  const handleLogout = () => {
    clearToken()
    navigate('/login')
  }

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'ClimaWatch Admin'

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-100 dark:bg-zinc-900">
      {/* Sidebar — always dark */}
      <aside
        className={[
          'relative shrink-0 flex flex-col bg-zinc-950 border-r border-zinc-800/60 transition-[width] duration-200',
          collapsed ? 'w-[60px]' : 'w-[220px]',
        ].join(' ')}
      >
        {/* Logo */}
        <div
          className={[
            'flex items-center gap-2.5 h-14 px-3 border-b border-zinc-800/60 shrink-0',
            collapsed ? 'justify-center' : '',
          ].join(' ')}
        >
          <div className="w-7 h-7 shrink-0 bg-emerald-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-[10px] tracking-tight">CW</span>
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-white font-semibold text-sm leading-tight tracking-tight">
                ClimaWatch
              </p>
              <p className="text-zinc-500 text-[10px] leading-tight">Admin Panel</p>
            </div>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto overflow-x-visible px-2 py-3 space-y-0.5">
          {NAV.map((item) => (
            <NavItem
              key={item.to}
              item={item}
              collapsed={collapsed}
              isActive={location.pathname === item.to}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="shrink-0 border-t border-zinc-800/60 p-2 space-y-0.5">
          {/* Sign out */}
          <div className="relative group/navitem">
            <button
              onClick={handleLogout}
              className={[
                'flex items-center gap-3 w-full rounded-lg px-3 py-2.5 text-zinc-400 hover:bg-white/5 hover:text-zinc-100 transition-all duration-150',
                collapsed ? 'justify-center' : '',
              ].join(' ')}
            >
              <LogOut size={18} className="shrink-0" />
              {!collapsed && (
                <span className="text-sm font-medium leading-none">Sign out</span>
              )}
            </button>
            {collapsed && (
              <div className="pointer-events-none absolute left-full top-1/2 z-50 ml-2 -translate-y-1/2 rounded-md border border-zinc-700 bg-zinc-800 px-2.5 py-1.5 text-xs font-medium text-white whitespace-nowrap shadow-xl opacity-0 transition-opacity duration-100 group-hover/navitem:opacity-100">
                Sign out
              </div>
            )}
          </div>

          {/* Collapse toggle */}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className={[
              'flex items-center gap-3 w-full rounded-lg px-3 py-2 text-zinc-600 hover:bg-white/5 hover:text-zinc-400 transition-all duration-150',
              collapsed ? 'justify-center' : '',
            ].join(' ')}
          >
            {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
            {!collapsed && (
              <span className="text-[11px] font-medium leading-none">Collapse sidebar</span>
            )}
          </button>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="shrink-0 h-14 bg-white dark:bg-zinc-950 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between px-5 gap-4">
          <h1 className="text-sm font-semibold text-slate-900 dark:text-white truncate">
            {pageTitle}
          </h1>
          <div className="flex items-center gap-2 shrink-0">
            <button className="p-2 rounded-lg text-slate-500 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors">
              <Bell size={16} />
            </button>
            <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center shrink-0">
              <span className="text-white text-xs font-bold select-none">A</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
