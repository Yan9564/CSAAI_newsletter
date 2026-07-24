from __future__ import annotations
import json, logging, os, re, time
from .models import Review
LOG=logging.getLogger(__name__)

KEYWORDS=re.compile(r'\b(multi-agent|agentic|llm agent|language model agent|orchestrat|coordination|tool-using|tool use|enterprise)\b', re.I)
EXCLUSIONS=re.compile(r'\b(chemical agent|biological agent|insurance agent|travel agent|real estate agent)\b', re.I)

def heuristic_review(paper) -> Review:
    text=f'{paper.title} {paper.abstract}'
    relevant=bool(KEYWORDS.search(text)) and not bool(EXCLUSIONS.search(text))
    score=4 if relevant else 1
    return Review(relevant, 'Heuristic review from title and abstract; no full-paper claims made.', score, score, 3 if relevant else 1, score, f"Based on metadata/abstract, this paper addresses {paper.title.lower()}.", ['agent coordination' if relevant else 'excluded non-AI agent usage'], 'Framework details require full-paper analysis beyond metadata.' if relevant else '', 'Potential implications are inferred only from the abstract.' if relevant else '', 'Service/management implications require full-paper review.' if relevant else '')

def openai_review(paper, config: dict) -> Review:
    if not os.getenv('OPENAI_API_KEY'):
        LOG.warning('OPENAI_API_KEY absent; using heuristic review')
        return heuristic_review(paper)
    from openai import OpenAI
    client=OpenAI(); model=config.get('openai',{}).get('model','gpt-4.1-mini')
    prompt=f"""Classify and score this arXiv paper for an academic newsletter on agentic AI/multi-agent systems. Use only metadata and abstract. Do not invent results, datasets, sample sizes, benchmarks, or performance figures. Return JSON keys: relevant boolean, rationale, relevance 0-5, novelty 0-5, methodological_quality 0-5, enterprise_service_relevance 0-5, summary, trends array, framework_notes, practical_implications, service_research_implications.\nTitle: {paper.title}\nAuthors: {', '.join(paper.authors)}\nCategory: {paper.primary_category}\nAbstract: {paper.abstract}"""
    for attempt in range(config.get('openai',{}).get('max_retries',4)):
        try:
            resp=client.responses.create(model=model, input=prompt, temperature=config.get('openai',{}).get('temperature',0.2))
            data=json.loads(resp.output_text)
            return Review(**data)
        except Exception as exc:
            if attempt == config.get('openai',{}).get('max_retries',4)-1:
                raise RuntimeError(f'OpenAI relevance review failed for {paper.arxiv_id}: {exc}')
            time.sleep(2**attempt)
