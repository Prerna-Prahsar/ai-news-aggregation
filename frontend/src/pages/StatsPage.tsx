import { useEffect, useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import { Loader2, BarChart2, Database, Star, Send } from 'lucide-react'
import toast from 'react-hot-toast'
import { fetchStats } from '../lib/api'
import type { DashboardStats } from '../types'

const COLORS = ['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b',
                 '#ef4444','#ec4899','#84cc16','#f97316','#6366f1']

function StatCard({ label, value, icon: Icon, color }: {
  label: string; value: string | number; icon: React.ElementType; color: string
}) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-slate-400">{label}</span>
        <div className={`w-8 h-8 rounded-lg ${color} flex items-center justify-center`}>
          <Icon size={15} />
        </div>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  )
}

export default function StatsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch(() => toast.error('Failed to load stats'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center py-24">
      <Loader2 size={28} className="animate-spin text-blue-400" />
    </div>
  )

  if (!stats) return null

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Insights</h1>
        <p className="text-sm text-slate-400">
          {stats.last_fetched
            ? `Last updated ${formatDistanceToNow(new Date(stats.last_fetched), { addSuffix: true })}`
            : 'Not yet fetched'}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Articles" value={stats.total_news.toLocaleString()}
          icon={Database} color="bg-blue-600/20 text-blue-400" />
        <StatCard label="Active Sources" value={stats.total_sources}
          icon={BarChart2} color="bg-purple-600/20 text-purple-400" />
        <StatCard label="Favorites" value={stats.total_favorites}
          icon={Star} color="bg-yellow-600/20 text-yellow-400" />
        <StatCard label="Broadcasts" value={stats.total_broadcasts}
          icon={Send} color="bg-emerald-600/20 text-emerald-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-100 mb-4">Articles by Source</h2>
          {stats.sources_breakdown.length === 0 ? (
            <p className="text-xs text-slate-500 py-8 text-center">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={stats.sources_breakdown} layout="vertical"
                margin={{ left: 8, right: 16, top: 0, bottom: 0 }}>
                <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis type="category" dataKey="source"
                  tick={{ fill: '#94a3b8', fontSize: 10 }} width={110} />
                <Tooltip contentStyle={{
                  background: '#1e293b', border: '1px solid #334155',
                  borderRadius: '8px', fontSize: 12, color: '#f1f5f9'
                }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-100 mb-4">Top Topics</h2>
          {stats.top_tags.length === 0 ? (
            <p className="text-xs text-slate-500 py-8 text-center">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={stats.top_tags.slice(0, 8)} dataKey="count" nameKey="tag"
                  cx="50%" cy="50%" outerRadius={80}
                  label={({ tag, percent }) =>
                    percent > 0.05 ? `${tag} ${(percent * 100).toFixed(0)}%` : ''}
                  labelLine={false}>
                  {stats.top_tags.slice(0, 8).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{
                  background: '#1e293b', border: '1px solid #334155',
                  borderRadius: '8px', fontSize: 12, color: '#f1f5f9'
                }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card p-5">
        <h2 className="text-sm font-semibold text-slate-100 mb-4">Topic Breakdown</h2>
        <div className="space-y-2">
          {stats.top_tags.map(({ tag, count }, i) => {
            const max = stats.top_tags[0]?.count || 1
            return (
              <div key={tag} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-28 truncate">{tag}</span>
                <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                  <div className="h-1.5 rounded-full"
                    style={{ width: `${(count / max) * 100}%`, background: COLORS[i % COLORS.length] }} />
                </div>
                <span className="text-xs text-slate-500 w-8 text-right">{count}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}