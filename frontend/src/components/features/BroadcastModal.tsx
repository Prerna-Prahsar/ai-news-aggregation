import { useState } from 'react'
import { X, Mail, Linkedin, MessageCircle, BookOpen, Send, CheckCircle2, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import type { Favorite, BroadcastPlatform } from '../../types'
import { sendBroadcast } from '../../lib/api'

interface Props {
favorite: Favorite
onClose: () => void
}

const PLATFORMS = [
{ id: 'email' as BroadcastPlatform, label: 'Email', icon: Mail, color: 'blue', hint: 'Send via SMTP' },
{ id: 'linkedin' as BroadcastPlatform, label: 'LinkedIn', icon: Linkedin, color: 'sky', hint: 'AI caption (simulated)' },
{ id: 'whatsapp' as BroadcastPlatform, label: 'WhatsApp', icon: MessageCircle, color: 'emerald', hint: 'Group sharing (simulated)' },
{ id: 'blog' as BroadcastPlatform, label: 'Blog', icon: BookOpen, color: 'purple', hint: 'Draft (simulated)' },
{ id: 'newsletter' as BroadcastPlatform, label: 'Newsletter', icon: Send, color: 'orange', hint: 'Queue (simulated)' },
]

const COLOR_MAP: Record<string, string> = {
blue: 'bg-blue-600/20 border-blue-600/40 text-blue-300 hover:bg-blue-600/30',
sky: 'bg-sky-600/20 border-sky-600/40 text-sky-300 hover:bg-sky-600/30',
emerald: 'bg-emerald-600/20 border-emerald-600/40 text-emerald-300 hover:bg-emerald-600/30',
purple: 'bg-purple-600/20 border-purple-600/40 text-purple-300 hover:bg-purple-600/30',
orange: 'bg-orange-600/20 border-orange-600/40 text-orange-300 hover:bg-orange-600/30',
}

export default function BroadcastModal({ favorite, onClose }: Props) {
const [selectedPlatform, setSelectedPlatform] = useState<BroadcastPlatform | null>(null)
const [recipients, setRecipients] = useState('')
const [loading, setLoading] = useState(false)
const [result, setResult] = useState<{ status: string; message: string } | null>(null)
const news = favorite.news_item

const handleBroadcast = async () => {
if (!selectedPlatform) return
setLoading(true)
try {
const recipientList = recipients.split(',').map(r => r.trim()).filter(Boolean)
const log = await sendBroadcast({ favorite_id: favorite.id, platform: selectedPlatform, recipients: recipientList })
setResult({ status: log.status, message: log.message || 'Broadcast completed.' })
toast.success('Broadcast done!')
} catch (e: any) {
toast.error(e?.response?.data?.detail || 'Broadcast failed')
} finally {
setLoading(false)
}
}

return (
<div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
<div className="card w-full max-w-md animate-fade-in">
<div className="flex items-center justify-between p-4 border-b border-slate-800">
<h2 className="font-semibold text-slate-100">Broadcast News</h2>
<button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
</div>
<div className="p-4 space-y-4">
<div className="bg-slate-800 rounded-lg p-3">
<p className="text-xs text-slate-400 mb-1">{news?.source?.name || 'Unknown Source'}</p>
<p className="text-sm font-medium text-slate-100 line-clamp-2">{news?.title}</p>
</div>
{!result ? (
<div className="space-y-4">
<div>
<p className="text-xs font-medium text-slate-400 mb-2">Choose Platform</p>
<div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
{PLATFORMS.map(p => {
const Icon = p.icon
const isSelected = selectedPlatform === p.id
return (
<button key={p.id} onClick={() => setSelectedPlatform(p.id)} className={`border rounded-lg p-3 text-left transition-all ${isSelected ? COLOR_MAP[p.color] : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}>
<Icon size={16} className="mb-1.5" />
<p className="text-xs font-medium">{p.label}</p>
<p className="text-[10px] opacity-70 mt-0.5">{p.hint}</p>
</button>
)
})}
</div>
</div>
{(selectedPlatform === 'email' || selectedPlatform === 'whatsapp') && (
<div>
<label className="text-xs font-medium text-slate-400 block mb-1">Recipients (comma-separated)</label>
<input className="input" placeholder={selectedPlatform === 'email' ? 'user@example.com' : '+91XXXXXXXXXX'} value={recipients} onChange={e => setRecipients(e.target.value)} />
</div>
)}
<button onClick={handleBroadcast} disabled={!selectedPlatform || loading} className="btn-primary w-full flex items-center justify-center gap-2">
{loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
{loading ? 'Sending…' : 'Broadcast'}
</button>
</div>
) : (
<div className="space-y-3">
<div className="flex items-center gap-2 text-emerald-400">
<CheckCircle2 size={18} />
<span className="text-sm font-medium capitalize">{result.status}</span>
</div>
<p className="text-sm text-slate-300">{result.message}</p>
<button onClick={onClose} className="btn-primary w-full">Done</button>
</div>
)}
</div>
</div>
</div>
)
}