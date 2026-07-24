import re

def validate_markdown(md: str, papers, cfg: dict) -> list[str]:
    errors=[]
    if not md.strip(): errors.append('empty newsletter output')
    ids=[p.arxiv_id.split('v')[0] for p in papers]
    if len(ids) != len(set(ids)): errors.append('duplicate papers')
    for p in papers:
        if not p.authors: errors.append(f'missing authors: {p.arxiv_id}')
        if not p.arxiv_id_url or not p.pdf_url: errors.append(f'missing links: {p.arxiv_id}')
    if md.count('```') % 2: errors.append('malformed Markdown: unclosed code fence')
    allowed = cfg.get('validation',{}).get('allow_numeric_metadata_only', True)
    if allowed:
        body='\n'.join(line for line in md.splitlines() if not any(k in line for k in ['arXiv ID','Submitted/updated','Ranking basis']))
        for pat in cfg.get('validation',{}).get('forbidden_unsupported_number_patterns',[]):
            if re.search(pat, body, re.I): errors.append(f'unsupported numerical statement matching {pat}')
    return errors
