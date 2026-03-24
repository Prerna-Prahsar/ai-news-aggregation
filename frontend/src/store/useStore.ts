import { create } from 'zustand'
import type { NewsItem, Favorite, DashboardStats } from '../types'

interface AppStore {
  newsItems: NewsItem[]
  setNewsItems: (items: NewsItem[]) => void
  updateNewsItem: (id: number, patch: Partial<NewsItem>) => void
  favorites: Favorite[]
  setFavorites: (favs: Favorite[]) => void
  addFavoriteLocal: (fav: Favorite) => void
  removeFavoriteLocal: (newsItemId: number) => void
  stats: DashboardStats | null
  setStats: (s: DashboardStats) => void
  isRefreshing: boolean
  setRefreshing: (v: boolean) => void
}

export const useStore = create<AppStore>((set) => ({
  newsItems: [],
  setNewsItems: items => set({ newsItems: items }),
  updateNewsItem: (id, patch) =>
    set(s => ({ newsItems: s.newsItems.map(n => n.id === id ? { ...n, ...patch } : n) })),
  favorites: [],
  setFavorites: favs => set({ favorites: favs }),
  addFavoriteLocal: fav => set(s => ({ favorites: [fav, ...s.favorites] })),
  removeFavoriteLocal: newsItemId =>
    set(s => ({ favorites: s.favorites.filter(f => f.news_item_id !== newsItemId) })),
  stats: null,
  setStats: s => set({ stats: s }),
  isRefreshing: false,
  setRefreshing: v => set({ isRefreshing: v }),
}))