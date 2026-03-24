import { useEffect, useState } from 'react'
import { Star, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { fetchFavorites } from '../lib/api'
import type { Favorite } from '../types'
import FavoriteCard from '../components/features/FavoriteCard'

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const data = await fetchFavorites()
      setFavorites(data)
    } catch {
      toast.error('Failed to load favorites')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleRemove = (id: number) => {
    setFavorites(f => f.filter(fav => fav.id !== id))
  }

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 bg-yellow-500/20 rounded-lg flex items-center justify-center">
          <Star size={18} className="text-yellow-400" fill="currentColor" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Favorites</h1>
          <p className="text-sm text-slate-400">
            {favorites.length} saved article{favorites.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin text-blue-400" />
        </div>
      ) : favorites.length === 0 ? (
        <div className="text-center py-24">
          <Star size={40} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-400 mb-1">No favorites yet</p>
          <p className="text-sm text-slate-500">Star articles in the Feed to save them here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {favorites.map(fav => (
            <FavoriteCard key={fav.id} favorite={fav} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </div>
  )
}