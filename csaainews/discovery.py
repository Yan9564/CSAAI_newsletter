from __future__ import annotations
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
import logging, time, urllib.request
from .models import Paper

LOG = logging.getLogger(__name__)

def parse_date(value: str) -> datetime:
    dt = parsedate_to_datetime(value) if ',' in value else datetime.fromisoformat(value.replace('Z','+00:00'))
    return dt.astimezone(timezone.utc)

def within_range(dt: datetime, days: int, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    return now - timedelta(days=days) <= dt <= now + timedelta(days=1)

def normalize_arxiv_id(raw: str) -> str:
    return raw.rsplit('/abs/', 1)[-1].split('v')[0] if '/abs/' in raw else raw.split('v')[0]

def build_query(topic: str, categories: list[str], exclusions: list[str]) -> str:
    cats = ' OR '.join(f'cat:{c}' for c in categories)
    excl = ' '.join(f'ANDNOT all:"{e}"' for e in exclusions)
    return f'(all:"{topic}" AND ({cats})) {excl}'

def entry_to_paper(entry) -> Paper:
    links = {getattr(l, 'type', ''): l.href for l in getattr(entry, 'links', [])}
    return Paper(
        arxiv_id=getattr(entry, 'id').rsplit('/abs/',1)[-1],
        title=' '.join(getattr(entry, 'title', '').split()),
        authors=[a.name for a in getattr(entry, 'authors', [])],
        abstract=' '.join(getattr(entry, 'summary', '').split()),
        submitted_date=parse_date(getattr(entry, 'published')),
        updated_date=parse_date(getattr(entry, 'updated', getattr(entry, 'published'))),
        arxiv_id_url=getattr(entry, 'id'),
        pdf_url=links.get('application/pdf', getattr(entry, 'id').replace('/abs/', '/pdf/')),
        primary_category=getattr(getattr(entry, 'arxiv_primary_category', None), 'term', ''),
    )

def fetch_arxiv(config: dict) -> list[Paper]:
    search = config['search']; papers = {}
    for topic in search['topics']:
        query = quote_plus(build_query(topic, search['arxiv_categories'], search.get('exclusions', [])))
        url = f"https://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={search.get('max_results_per_topic',50)}"
        for attempt in range(3):
            try:
                LOG.info('Fetching arXiv topic=%s attempt=%s', topic, attempt+1)
                import feedparser
                with urllib.request.urlopen(url, timeout=30) as resp:
                    payload = resp.read()
                feed = feedparser.parse(payload)
                for entry in feed.entries:
                    paper = entry_to_paper(entry)
                    if within_range(paper.submitted_date, search.get('date_range_days', 7)) or within_range(paper.updated_date, search.get('date_range_days', 7)):
                        papers[paper.arxiv_id] = paper
                break
            except Exception as exc:
                if attempt == 2: raise RuntimeError(f'arXiv request failed for {topic}: {exc}')
                time.sleep(2 ** attempt)
        time.sleep(3)
    return list(papers.values())[: search.get('paper_limit', 12)]

def load_sample(config: dict) -> list[Paper]:
    from .config import load_yaml
    return [Paper(**{**p, 'submitted_date': datetime.fromisoformat(p['submitted_date'].replace('Z','+00:00')), 'updated_date': datetime.fromisoformat(p['updated_date'].replace('Z','+00:00'))}) for p in load_yaml(config)['papers']]
