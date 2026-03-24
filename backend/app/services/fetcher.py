import asyncio
import aiohttp
import feedparser
import hashlib
import re
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

AI_SOURCES = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog", "feed_url": "https://openai.com/blog/rss.xml", "type": "rss"},
    {"name": "Google AI Blog", "url": "https://ai.googleblog.com", "feed_url": "https://feeds.feedburner.com/blogspot/gJZg", "type": "rss"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/news", "feed_url": "https://www.anthropic.com/rss.xml", "type": "rss"},
    {"name": "DeepMind Blog", "url": "https://deepmind.com/blog", "feed_url": "https://deepmind.com/blog/feed/basic", "type": "rss"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog", "feed_url": "https://huggingface.co/blog/feed.xml", "type": "rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence", "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai", "feed_url": "https://venturebeat.com/category/ai/feed/", "type": "rss"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence", "feed_url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "rss"},
    {"name": "Wired AI", "url": "https://www.wired.com/tag/artificial-intelligence", "feed_url": "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss", "type": "rss"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com", "feed_url": "https://www.technologyreview.com/feed/", "type": "rss"},
    {"name": "Microsoft AI Blog", "url": "https://blogs.microsoft.com/ai", "feed_url": "https://blogs.microsoft.com/ai/feed/", "type": "rss"},
    {"name": "Meta AI Blog", "url": "https://ai.meta.com/blog", "feed_url": "https://ai.meta.com/blog/feed/", "type": "rss"},
    {"name": "arXiv cs.AI", "url": "https://arxiv.org/list/cs.AI/recent", "feed_url": "https://rss.arxiv.org/rss/cs.AI", "type": "rss"},
    {"name": "arXiv cs.LG", "url": "https://arxiv.org/list/cs.LG/recent", "feed_url": "https://rss.arxiv.org/rss/cs.LG", "type": "rss"},
    {"name": "Hacker News AI", "url": "https://news.ycombinator.com", "feed_url": "https://hnrss.org/newest?q=AI+LLM+machine+learning&points=10", "type": "rss"},
    {"name": "Papers With Code", "url": "https://paperswithcode.com", "feed_url": "https://paperswithcode.com/latest.xml", "type": "rss"},
    {"name": "Stability AI Blog", "url": "https://stability.ai/blog", "feed_url": "https://stability.ai/blog?format=rss", "type": "rss"},
    {"name": "Y Combinator Blog", "url": "https://www.ycombinator.com/blog", "feed_url": "https://www.ycombinator.com/blog/rss.xml", "type": "rss"},
    {"name": "Reddit r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning", "feed_url": "https://www.reddit.com/r/MachineLearning/top.json?t=day&limit=10", "type": "api"},
    {"name": "Product Hunt AI", "url": "https://www.producthunt.com/topics/artificial-intelligence", "feed_url": "https://www.producthunt.com/feed?category=artificial-intelligence", "type": "rss"},
]

AI_KEYWORDS = [
    "AI", "artificial intelligence", "machine learning", "LLM", "GPT",
    "neural network", "deep learning", "NLP", "transformer", "ChatGPT",
    "generative AI", "foundation model", "diffusion model", "RLHF",
    "fine-tuning", "Claude", "Gemini", "Llama", "RAG", "AGI"
]


def extract_tags(text: str) -> List[str]:
    found = []
    text_lower = text.lower()
    for kw in AI_KEYWORDS:
        if kw.lower() in text_lower:
            found.append(kw)
    return list(set(found))[:8]


def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)[:500]


def parse_date(entry) -> Optional[datetime]:
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(tz=timezone.utc)


def compute_impact_score(title: str, summary: str) -> float:
    high_impact_words = ["breakthrough", "launch", "released", "new", "announce",
                         "GPT-5", "Claude 3", "open source", "paper", "research",
                         "raises", "billion", "acqui"]
    text = (title + " " + summary).lower()
    score = 0.4
    for word in high_impact_words:
        if word.lower() in text:
            score += 0.06
    return min(round(score, 2), 1.0)


async def fetch_rss_feed(source: Dict) -> List[Dict]:
    results = []
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "AI-News-Dashboard/1.0"},
        ) as session:
            async with session.get(source["feed_url"]) as resp:
                if resp.status != 200:
                    return []
                content = await resp.text()

        feed = feedparser.parse(content)
        for entry in feed.entries[:15]:
            title = getattr(entry, "title", "").strip()
            url = getattr(entry, "link", "").strip()
            if not title or not url:
                continue
            summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
            summary = clean_html(summary_raw)
            results.append({
                "title": title,
                "summary": summary,
                "url": url,
                "author": getattr(entry, "author", None),
                "published_at": parse_date(entry),
                "tags": extract_tags(title + " " + summary),
                "impact_score": compute_impact_score(title, summary),
            })
    except Exception as e:
        logger.error(f"Error fetching RSS {source['name']}: {e}")
    return results


async def fetch_reddit_feed(source: Dict) -> List[Dict]:
    results = []
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "AI-News-Dashboard/1.0"},
        ) as session:
            async with session.get(source["feed_url"]) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()

        posts = data.get("data", {}).get("children", [])
        for post in posts[:10]:
            p = post.get("data", {})
            title = p.get("title", "").strip()
            url = p.get("url", "").strip()
            if not title or not url:
                continue
            created = datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc)
            results.append({
                "title": title,
                "summary": p.get("selftext", "")[:300] or f"Posted on Reddit with {p.get('score', 0)} upvotes.",
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "author": p.get("author"),
                "published_at": created,
                "tags": extract_tags(title),
                "impact_score": min(1.0, p.get("score", 0) / 500),
            })
    except Exception as e:
        logger.error(f"Error fetching Reddit: {e}")
    return results


async def fetch_all_sources() -> List[Dict]:
    tasks = []
    source_map = {}
    for idx, source in enumerate(AI_SOURCES):
        source_map[idx] = source
        if source["type"] == "api" and "reddit" in source["feed_url"]:
            tasks.append(fetch_reddit_feed(source))
        else:
            tasks.append(fetch_rss_feed(source))

    results_nested = await asyncio.gather(*tasks, return_exceptions=True)
    all_items = []
    for idx, result in enumerate(results_nested):
        if isinstance(result, Exception):
            continue
        for item in result:
            item["source_name"] = source_map[idx]["name"]
            all_items.append(item)

    logger.info(f"Fetched {len(all_items)} raw items from {len(AI_SOURCES)} sources")
    return all_items