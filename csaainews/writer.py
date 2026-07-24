from datetime import date

def render_newsletter(issue_date: date, ranked: list[tuple[object, object]], cfg: dict) -> str:
    title=cfg.get('publication',{}).get('issue_title','CSAAI Agentic AI Weekly')
    lines=[f"# {title} — {issue_date.isoformat()}", '', '> This issue is generated from arXiv metadata and abstracts plus OpenAI-assisted relevance review. Claims that would require full-paper analysis are explicitly labeled as requiring full-paper review.', '', '## Executive overview', '']
    if not ranked:
        lines += ['No newly discovered papers passed the relevance and quality filters for this issue.', '']
    else:
        lines += [f'This issue highlights {len(ranked)} newly discovered arXiv paper(s) relevant to agentic AI, multi-agent systems, or enterprise/service applications. Summaries are based on titles, author lists, categories, submission dates, and abstracts.', '']
    trends=sorted({t for _,r in ranked for t in r.trends})
    lines += ['## Major research trends', ''] + ([f'- {t}' for t in trends] or ['- No cross-paper trend can be supported from the available metadata/abstracts.']) + ['']
    lines += ['## Selected papers', '']
    for i,(p,r) in enumerate(ranked,1):
        lines += [f'### {i}. {p.title}', '', f'**Authors:** {", ".join(p.authors)}  ', f'**arXiv ID:** [{p.arxiv_id}]({p.arxiv_id_url})  ', f'**PDF:** [Download PDF]({p.pdf_url})  ', f'**Category:** {p.primary_category}  ', f'**Submitted/updated:** {p.submitted_date.date().isoformat()} / {p.updated_date.date().isoformat()}  ', f'**Ranking basis:** relevance={r.relevance}/5, novelty={r.novelty}/5, methodological quality visible from abstract={r.methodological_quality}/5, enterprise/service relevance={r.enterprise_service_relevance}/5.  ', '', '**Metadata/abstract-based summary:**', r.summary, '', '**Technical framework explanation:**', r.framework_notes or 'Framework specifics require full-paper analysis.', '', '**Practical implications:**', r.practical_implications or 'Practical implications require full-paper analysis.', '', '**Implications for service and management researchers:**', r.service_research_implications or 'Service and management implications require full-paper analysis.', '', '**Full-paper analysis boundary:** This newsletter has not verified experimental results, datasets, sample sizes, benchmarks, or performance figures beyond the abstract metadata.', '']
    lines += ['## Method note', '', 'The pipeline deduplicates by arXiv ID, applies configured topic and exclusion filters, asks OpenAI to review relevance rather than relying on keyword matches alone, and validates generated Markdown before publication.', '']
    return '\n'.join(lines)
