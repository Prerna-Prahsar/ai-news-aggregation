import { useEffect, useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Rss, ToggleLeft, ToggleRight, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { fetchSources, toggleSource, seedAndFetch } from '../lib/api'
import type { Source } from '../types'

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const data = await fetchSources()
      setSources(data)
    } catch {
      toast.error('Failed to load sources')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleToggle = async (id: number) => {
    try {
      const result = await toggleSource(id)
      setSources(s => s.map(src => src.id === id ? { ...src, active: result.active } : src))
    } catch {
      toast.error('Failed to toggle source')
    }
  }

  const handleSeed = async () => {
    setSeeding(true)
    try {
      await seedAndFetch()
      toast.success('Sources seeded and fetch started!')
      setTimeout(load, 2000)
    } catch {
      toast.error('Seed failed')
    } finally {
      setSeeding(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white">News Sources</h1>
          <p className="text-sm text-slate-400">
            {sources.filter(s => s.active).length} of {sources.length} active
          </p>
        </div>
        <button onClick={handleSeed} disabled={seeding}
          className="btn-primary flex items-center gap-2">
          {seeding ? <Loader2 size={14} className="animate-spin" /> : <Rss size={14} />}
          Seed & Fetch All
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin text-blue-400" />
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Source</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 hidden sm:table-cell">Type</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 hidden md:table-cell">Last Fetched</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Status</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Toggle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {sources.map(src => (
                <tr key={src.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-200">{src.name}</p>
                    <a href={src.url} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:underline truncate block max-w-[200px]">
                      {src.url}
                    </a>
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <span className="badge bg-slate-800 text-slate-400">{src.type}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400 hidden md:table-cell">
                    {src.last_fetched
                      ? formatDistanceToNow(new Date(src.last_fetched), { addSuffix: true })
                      : 'Never'}
                  </td>
                  <td className="px-4 py-3">
                    {src.active ? (
                      <span className="flex items-center gap-1 text-xs text-emerald-400">
                        <CheckCircle2 size={12} /> Active
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <XCircle size={12} /> Disabled
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => handleToggle(src.id)}>
                      {src.active
                        ? <ToggleRight size={22} className="text-emerald-400 hover:text-emerald-300" />
                        : <ToggleLeft size={22} className="text-slate-600 hover:text-slate-400" />}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}