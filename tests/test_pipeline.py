from datetime import datetime, timezone, timedelta, date
from csaainews.discovery import build_query, within_range
from csaainews.models import Paper, Review
from csaainews.store import dedupe_new
from csaainews.writer import render_newsletter
from csaainews.validate import validate_markdown

def paper(id='1234.1v1', authors=None):
    return Paper(id, 'LLM Agent Coordination', authors or ['A'], 'Multi-agent orchestration abstract.', datetime(2026,7,20,tzinfo=timezone.utc), datetime(2026,7,20,tzinfo=timezone.utc), f'https://arxiv.org/abs/{id}', f'https://arxiv.org/pdf/{id}', 'cs.AI')

def test_build_query_has_topics_categories_and_exclusions():
    q=build_query('LLM agents', ['cs.AI'], ['chemical agent'])
    assert 'all:"LLM agents"' in q and 'cat:cs.AI' in q and 'ANDNOT all:"chemical agent"' in q

def test_dedupe_new_uses_base_arxiv_id():
    assert dedupe_new([paper('1234.1v1'), paper('1234.1v2')], {'9999.1'}) == [paper('1234.1v1')]
    assert dedupe_new([paper('1234.1v1')], {'1234.1'}) == []

def test_within_range_handles_utc_dates():
    now=datetime(2026,7,24,tzinfo=timezone.utc)
    assert within_range(now-timedelta(days=3), 7, now)
    assert not within_range(now-timedelta(days=8), 7, now)

def test_markdown_generation_and_validation():
    p=paper(); r=Review(True,'ok',5,4,3,4,'Summary from abstract',['agent orchestration'],'Framework from abstract','Practical implication','Service implication')
    md=render_newsletter(date(2026,7,24), [(p,r)], {'publication': {'issue_title':'Test'}})
    assert '# Test' in md and 'Full-paper analysis boundary' in md and 'https://arxiv.org/abs/' in md
    assert validate_markdown(md, [p], {'validation': {'allow_numeric_metadata_only': True, 'forbidden_unsupported_number_patterns': ['\\b\\d+%\\b']}}) == []
