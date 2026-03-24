import re
import math
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

THRESHOLD = 0.82


def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "is", "are", "was", "were", "be",
        "has", "have", "had", "this", "that", "it", "its", "from", "as",
        "how", "what", "when", "why", "who", "which", "will", "can",
        "about", "after", "before", "into", "over", "under", "new"
    }
    return [t for t in tokens if t not in stop_words and len(t) > 2]


def compute_tfidf(docs: List[List[str]]) -> List[Dict[str, float]]:
    N = len(docs)
    if N == 0:
        return []
    df: Dict[str, int] = Counter()
    for tokens in docs:
        for term in set(tokens):
            df[term] += 1
    vectors = []
    for tokens in docs:
        tf = Counter(tokens)
        total = len(tokens) or 1
        vec: Dict[str, float] = {}
        for term, count in tf.items():
            term_tf = count / total
            term_idf = math.log((N + 1) / (df[term] + 1)) + 1
            vec[term] = term_tf * term_idf
        vectors.append(vec)
    return vectors


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a.keys()) & set(vec_b.keys())
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def deduplicate(items: List[Dict]) -> Tuple[List[Dict], int]:
    if not items:
        return [], 0

    seen_urls = {}
    url_deduped = []
    for item in items:
        url = item.get("url", "").strip().lower()
        if url and url not in seen_urls:
            seen_urls[url] = True
            url_deduped.append(item)

    texts = [tokenize(item.get("title", "") + " " + (item.get("summary") or ""))
             for item in url_deduped]
    vectors = compute_tfidf(texts)

    duplicate_flags = [False] * len(url_deduped)
    duplicate_count = 0

    for i in range(len(url_deduped)):
        if duplicate_flags[i]:
            continue
        for j in range(i + 1, len(url_deduped)):
            if duplicate_flags[j]:
                continue
            sim = cosine_similarity(vectors[i], vectors[j])
            if sim >= THRESHOLD:
                duplicate_flags[j] = True
                url_deduped[j]["is_duplicate"] = True
                url_deduped[j]["duplicate_of_title"] = url_deduped[i]["title"]
                duplicate_count += 1

    for item in url_deduped:
        if "is_duplicate" not in item:
            item["is_duplicate"] = False

    return url_deduped, duplicate_count