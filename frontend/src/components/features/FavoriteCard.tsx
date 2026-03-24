import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { ExternalLink, Trash2, Send } from 'lucide-react'
import toast from 'react-hot-toast'
import type { Favorite } from '../../types'
import { removeFavorite } from '../../lib/api'
import BroadcastModal from './BroadcastModal'

interface Props {
  favorite: Favorite
  onRemove: (id: number) => void
}

export default function FavoriteCard({ favorite, onRemove }: Props) {
  const [showBroadcast, setShowBroadcast] = useState(false)
  const [removing, setRemoving] = useState(false)
  const news = favorite.news_item

  if (!news) return null

  const handleRemove = async () => {
    setRemoving(true)
    try {
      await removeFavorite(favorite.id)
      onRemove(favorite.id)
      toast.success('Removed from favorites')
    } catch {
      toast.error('Failed to remove')
    } finally {
      setRemoving(false)
    }
  }

  return (
    <div>
      <article className="card p-4 hover:border-slate-700 transition-colors animate-fade-in">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            {news.source && (
              <span className="badge bg-slate-800 text-slate-300 text-xs">
                {news.source.name}
              </span>
            )}
            <span className="text-xs text-slate-500">
              {news.published_at ? formatDistanceToNow(new Date(news.published_at), { addSuffix: true }) : 'recently'}
            </span>
          </div>
        </div>

        <h3 className="text-sm font-semibold text-slate-100 leading-snug mb-2 line-clamp-2">
          {news.title}
        </h3>

        {news.summary && (
          <p className="text-xs text-slate-400 line-clamp-2 mb-3">
            {news.summary}
          </p>
        )}

        {news.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {news.tags.slice(0, 4).map(tag => (
              <span key={tag} className="badge bg-slate-800 text-slate-400 text-[10px]">
                #{tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
          <a href={news.url} target="_blank" rel="noopener noreferrer" className="btn-ghost flex items-center gap-1.5 text-xs">
            <ExternalLink size={13} />
            Read
          </a>
          <button onClick={() => setShowBroadcast(true)} className="btn-primary flex items-center gap-1.5 text-xs py-1.5">
            <Send size={13} />
            Broadcast
          </button>
          <button onClick={handleRemove} disabled={removing} className="btn-ghost flex items-center gap-1.5 text-xs ml-auto text-red-400 hover:text-red-300">
            <Trash2 size={13} />
          </button>
        </div>
      </article>

      {showBroadcast && (
        <BroadcastModal favorite={favorite} onClose={() => setShowBroadcast(false)} />
      )}
    </div>
  )
}