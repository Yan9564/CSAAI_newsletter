import json
from pathlib import Path

def load_processed(path: str | Path) -> set[str]:
    p=Path(path)
    if not p.exists(): return set()
    return set(json.loads(p.read_text(encoding='utf-8')).get('processed_arxiv_ids', []))

def dedupe_new(papers, processed: set[str]):
    seen=set(); out=[]
    for p in papers:
        base=p.arxiv_id.split('v')[0]
        if base not in processed and base not in seen:
            out.append(p); seen.add(base)
    return out

def save_processed(path: str | Path, existing: set[str], papers):
    ids=sorted(existing | {p.arxiv_id.split('v')[0] for p in papers})
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps({'processed_arxiv_ids': ids}, indent=2)+'\n', encoding='utf-8')
