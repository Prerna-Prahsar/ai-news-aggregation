import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Newspaper, Star, BarChart2, Rss, Bot } from 'lucide-react'
import FeedPage from './pages/FeedPage'
import FavoritesPage from './pages/FavoritesPage'
import StatsPage from './pages/StatsPage'
import SourcesPage from './pages/SourcesPage'

const navItems = [
  { to: '/',          label: 'Feed',      icon: Newspaper },
  { to: '/favorites', label: 'Favorites', icon: Star      },
  { to: '/stats',     label: 'Insights',  icon: BarChart2 },
  { to: '/sources',   label: 'Sources',   icon: Rss       },
]

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#1e293b', color: '#f1f5f9', border: '1px solid #334155' },
        }}
      />
      <div className="flex h-screen overflow-hidden">
        <aside className="w-56 shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col">
          <div className="px-5 py-5 border-b border-slate-800 flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot size={18} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-none">AI News</p>
              <p className="text-xs text-slate-400">Dashboard</p>
            </div>
          </div>
          <nav className="flex-1 px-3 py-4 space-y-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 font-medium'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
                  }`
                }
              >
                <Icon size={17} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="px-5 py-4 border-t border-slate-800">
            <p className="text-xs text-slate-600">v1.0 — MVP</p>
          </div>
        </aside>
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <Routes>
            <Route path="/"          element={<FeedPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/stats"     element={<StatsPage />} />
            <Route path="/sources"   element={<SourcesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}