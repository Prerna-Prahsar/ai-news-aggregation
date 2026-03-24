# 🤖 AI News Intelligence Dashboard  
**MVP v1.0 — Developed by Prerna Prashar**

---

## 🌐 Live Application

| Component | Link |
|----------|------|
| Frontend Dashboard | https://ainews-frontend-2itq.onrender.com |
| Backend API | https://ai-news-dashboard-3y3h.onrender.com |
| API Documentation | https://ai-news-dashboard-3y3h.onrender.com/docs |

---

## 📌 Project Summary

This project is a full-stack AI-powered news intelligence system designed to continuously collect, process, and present AI-related news from multiple sources in a structured and user-friendly way.

The platform automates:
- News aggregation from 20+ AI sources  
- Content cleaning and normalization  
- Duplicate detection using semantic similarity  
- Smart tagging and impact scoring  
- Multi-platform sharing of curated content  

---

## 🚀 Key Functionalities

- Automated news fetching at regular intervals  
- Duplicate removal using TF-IDF cosine similarity  
- Intelligent tag extraction  
- Impact-based ranking system  
- Search and filtering by tags  
- Save and manage favorite articles  
- Share content across:
  - Email  
  - LinkedIn (auto-caption generation)  
  - WhatsApp  
  - Blog / Newsletter  
- Analytics dashboard with visual insights  
- Admin panel for managing sources  

---

## 🧰 Technology Stack

### Frontend
- React 18  
- TypeScript  
- Tailwind CSS  
- Vite  
- Zustand  
- Recharts  

### Backend
- FastAPI (Python 3.11)  
- SQLAlchemy (async)  
- Pydantic  

### Database
- PostgreSQL  

### Data Processing
- aiohttp (async fetching)  
- BeautifulSoup  
- feedparser  

### Deployment
- Render (Frontend + Backend + DB)  

---

## 🏗️ System Workflow

```
[AI News Sources (RSS/APIs)]
        ↓
[Async Fetcher Service]
        ↓
[Data Processing Layer]
   - Cleaning
   - Tag extraction
   - Impact scoring
        ↓
[Deduplication Engine]
   - URL matching
   - TF-IDF similarity
        ↓
[PostgreSQL Database]
        ↓
[FastAPI Backend]
        ↓
[React Dashboard]
        ↓
[Broadcast Channels]
(Email | LinkedIn | WhatsApp | Blog)
```

---

## 🗄️ Database Design

Core tables include:

- sources → stores news providers  
- news_items → processed articles with metadata  
- favorites → saved articles by users  
- broadcast_logs → track shared content  
- users → user details  

---

## 📰 Integrated Sources

The system aggregates from platforms such as:

- OpenAI Blog  
- Google AI  
- Anthropic  
- DeepMind  
- Hugging Face  
- TechCrunch AI  
- MIT Tech Review  
- arXiv (AI/ML)  
- Hacker News  
- Reddit (ML community)  
- Product Hunt  

…and more (20+ total sources)

---

## ⚙️ Local Setup Guide

### Requirements
- Python 3.11  
- Node.js (18+)  
- PostgreSQL  

---

### Backend Setup

```bash
cd backend
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

set DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ainews

uvicorn app.main:app --reload --port 8000
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

---

## 🐳 Docker Setup (Optional)

```bash
git clone <your-repo-url>
cd ai-news-dashboard
cp .env.example .env
docker-compose up --build
```

---

## 📡 API Highlights

| Method | Endpoint | Description |
|--------|--------|-------------|
| GET | /api/news | Fetch news feed |
| GET | /api/news/{id} | Single article |
| POST | /api/news/refresh | Refresh data |
| GET | /api/favorites | User favorites |
| POST | /api/broadcast | Share content |
| GET | /api/admin/stats | Analytics |

---

## 📣 Broadcast Integration

- Email → SMTP supported  
- LinkedIn → Caption generation (extendable via OAuth)  
- WhatsApp → Can integrate with Twilio API  
- Newsletter → Mailchimp / Beehiiv compatible  

---

## 🎯 Highlights & Strengths

- Clean modular architecture  
- Efficient data deduplication using NLP  
- Fully responsive UI  
- Real-world deployment on cloud  
- Scalable backend with async processing  
- End-to-end pipeline from ingestion to visualization  

---

## 👩‍💻 Author

Prerna Prashar  

---

## 🏁 Final Note

This project demonstrates the integration of AI/NLP techniques, scalable backend systems, and modern frontend frameworks to build a production-ready intelligent content platform.
