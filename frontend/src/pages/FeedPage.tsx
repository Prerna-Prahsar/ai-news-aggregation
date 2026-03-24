import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, Search, X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { fetchNews, refreshNews, fetchTags } from '../lib/api'
import { useStore } from '../store/useStore'
import NewsCard from '../components/features/NewsCard'
import type { NewsListOut } from '../types'

const SORT_OPTIONS = [
  { value: 'date',   label: 'Latest' },
  { value: 'impact', label: 'Impact' },
  { value: 'source', label: 'Source' },
]

export default function FeedPage() {
  const { newsItems, setNewsItems, isRefreshing, setRefreshing } = useStore()
  const [data, setData] = useState<NewsListOut | null>(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [sort, setSort] = useState<'date' | 'impact' | 'source'>('date')
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const [tags, setTags] = useState<{ tag: string; count: number }[]>([])
  const [loading, setLoading] = useState(false)

  const loadNews = useCallback(async () => {
    setLoading(true)
    try {
      const result = await fetchNews({
        page,
        per_page: 24,
        search: search || undefined,
        tag: selectedTag || undefined,
        sort,
      })
      setData(result)
      setNewsItems(result.items)
    } catch {
      toast.error('Failed to load news')
    } finally {
      setLoading(false)
    }
  }, [page, search, sort, selectedTag])

  useEffect(() => { loadNews() }, [loadNews])
  useEffect(() => { fetchTags().then(setTags).catch(() => {}) }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refreshNews()
      toast.success('Refresh started! New items will appear shortly.')
      setTimeout(loadNews, 3000)
    } catch {
      toast.error('Refresh failed')
    } finally {
      setRefreshing(false)
    }
  }

  const handleSearch = () => { setSearch(searchInput); setPage(1) }
  const clearSearch = () => { setSearch(''); setSearchInput(''); setPage(1) }
  const totalPages = data ? Math.ceil(data.total / 24) : 1

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white">AI News Feed</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            {data ? `${data.total.toLocaleString()} articles from 20+ sources` : 'Loading…'}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-5">
        <div className="flex gap-2 flex-1 min-w-64">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              className="input pl-9"
              placeholder="Search news…"
              value={searchInput}
              onChange={e => setSearchInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
            />
            {searchInput && (
              <button
                onClick={clearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                <X size={13} />
              </button>
            )}
          </div>
          <button onClick={handleSearch} className="btn-primary px-3">
            <Search size={14} />
          </button>
        </div>
        <select
          className="input w-36"
          value={sort}
          onChange={e => { setSort(e.target.value as any); setPage(1) }}
        >
          {SORT_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-5">
          <button
            onClick={() => { setSelectedTag(null); setPage(1) }}
            className={`badge cursor-pointer transition-colors ${
              !selectedTag ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            All
          </button>
          {tags.slice(0, 15).map(({ tag, count }) => (
            <button
              key={tag}
              onClick={() => { setSelectedTag(tag === selectedTag ? null : tag); setPage(1) }}
              className={`badge cursor-pointer transition-colors ${
                selectedTag === tag
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {tag} <span className="ml-1 opacity-60">{count}</span>
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin text-blue-400" />
        </div>
      ) : newsItems.length === 0 ? (
        <div className="text-center py-24">
          <p className="text-slate-400 mb-3">No news yet.</p>
          <button onClick={handleRefresh} className="btn-primary">Fetch News Now</button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {newsItems.map(item => (
              <NewsCard key={item.id} item={item} onFavoriteChange={loadNews} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-ghost disabled:opacity-30"
              >
                ← Prev
              </button>
              <span className="text-sm text-slate-400">Page {page} of {totalPages}</span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-ghost disabled:opacity-30"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}