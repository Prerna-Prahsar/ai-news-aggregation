import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Star, ExternalLink, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import type { NewsItem } from '../../types'
import { addFavorite, removeFavoriteByNews } from '../../lib/api'
import { useStore } from '../../store/useStore'

interface Props {
  item: NewsItem
  onFavoriteChange?: () => void
}

const IMPACT_COLOR = (score: number) => {
  if (score >= 0.75) return 'text-emerald-400'
  if (score >= 0.5) return 'text-yellow-400'
  return 'text-slate-500'
}

const SOURCE_COLORS: Record<string, string> = {
  'OpenAI Blog': 'bg-emerald-900/40 text-emerald-300',
  'Google AI Blog': 'bg-blue-900/40 text-blue-300',
  'Anthropic Blog': 'bg-purple-900/40 text-purple-300',
  'TechCrunch AI': 'bg-orange-900/40 text-orange-300',
  'arXiv cs.AI': 'bg-rose-900/40 text-rose-300',
  'arXiv cs.LG': 'bg-rose-900/40 text-rose-300',
  'Hacker News AI': 'bg-amber-900/40 text-amber-300',
}

export default function NewsCard({ item, onFavoriteChange }: Props) {
  const [loading, setLoading] = useState(false)
  const { updateNewsItem } = useStore()

  const sourceBadge = item.source ? SOURCE_COLORS[item.source.name] || 'bg-slate-800 text-slate-300' : 'bg-slate-800 text-slate-300'

  const timeAgo = item.published_at ? formatDistanceToNow(new Date(item.published_at), { addSuffix: true }) : 'recently'

  const toggleFavorite = async () => {
    setLoading(true)
    try {
      if (item.is_favorited) {
        await removeFavoriteByNews(item.id)
        updateNewsItem(item.id, { is_favorited: false })
        toast.success('Removed from favorites')
      } else {
        await addFavorite(item.id)
        updateNewsItem(item.id, { is_favorited: true })
        toast.success('Added to favorites ⭐')
      }
      onFavoriteChange?.()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error updating favorites')
    } finally {
      setLoading(false)
    }
  }

  return (
    <article className="card p-4 hover:border-slate-700 transition-colors animate-fade-in">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {item.source && (
            <span className={`badge ${sourceBadge}`}>
              {item.source.name}
            </span>
          )}
          <span className="text-xs text-slate-500">{timeAgo}</span>
          {item.is_duplicate && (
            <span className="badge bg-yellow-900/40 text-yellow-400">duplicate</span>
          )}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <Zap size={12} className={IMPACT_COLOR(item.impact_score)} />
          <span className="text-xs text-slate-500">{Math.round(item.impact_score * 100)}%</span>
        </div>
      </div>

      <h3 className="text-sm font-semibold text-slate-100 leading-snug mb-1.5 line-clamp-2">
        {item.title}
      </h3>

      {item.summary && (
        <p className="text-xs text-slate-400 line-clamp-2 mb-3">
          {item.summary}
        </p>
      )}

      {item.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {item.tags.slice(0, 4).map(tag => (
            <span key={tag} className="badge bg-slate-800 text-slate-400 text-[10px]">
              #{tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
        <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn-ghost flex items-center gap-1.5 text-xs">
          <ExternalLink size={13} />
          Read
        </a>
        <button onClick={toggleFavorite} disabled={loading} className={`btn-ghost flex items-center gap-1.5 text-xs ml-auto ${item.is_favorited ? 'text-yellow-400 hover:text-yellow-300' : ''}`}>
          <Star size={13} fill={item.is_favorited ? 'currentColor' : 'none'} />
          {item.is_favorited ? 'Saved' : 'Save'}
        </button>
      </div>
    </article>
  )
}