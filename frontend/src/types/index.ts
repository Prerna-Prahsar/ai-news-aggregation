export interface Source {
  id: number
  name: string
  url: string
  feed_url?: string
  type: 'rss' | 'api' | 'scraper'
  active: boolean
  last_fetched?: string
  created_at: string
}

export interface NewsItem {
  id: number
  source_id: number
  source?: Source
  title: string
  summary?: string
  url: string
  author?: string
  published_at?: string
  tags: string[]
  is_duplicate: boolean
  is_favorited: boolean
  impact_score: number
  image_url?: string
  created_at: string
}

export interface NewsListOut {
  items: NewsItem[]
  total: number
  page: number
  per_page: number
}

export interface Favorite {
  id: number
  news_item_id: number
  news_item?: NewsItem
  created_at: string
}

export type BroadcastPlatform = 'email' | 'linkedin' | 'whatsapp' | 'blog' | 'newsletter'

export interface BroadcastLog {
  id: number
  favorite_id: number
  platform: BroadcastPlatform
  status: 'pending' | 'sent' | 'failed' | 'simulated'
  message?: string
  recipients: string[]
  timestamp: string
}

export interface DashboardStats {
  total_news: number
  total_sources: number
  total_favorites: number
  total_broadcasts: number
  last_fetched?: string
  top_tags: { tag: string; count: number }[]
  sources_breakdown: { source: string; count: number }[]
}