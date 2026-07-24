from __future__ import annotations
import argparse, json, logging, shutil
from datetime import date
from pathlib import Path
from .config import load_yaml
from .discovery import fetch_arxiv, load_sample
from .store import load_processed, dedupe_new, save_processed
from .review import openai_review
from .writer import render_newsletter
from .validate import validate_markdown
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
LOG=logging.getLogger(__name__)

def update_readme(path: Path, issue_path: Path):
    text=path.read_text(encoding='utf-8') if path.exists() else '# CSAAI_newsletter\n'
    block=f'<!-- latest-newsletter:start -->\nLatest newsletter: [{issue_path.name}]({issue_path.as_posix()})\n<!-- latest-newsletter:end -->'
    if '<!-- latest-newsletter:start -->' in text:
        import re; text=re.sub(r'<!-- latest-newsletter:start -->.*?<!-- latest-newsletter:end -->', block, text, flags=re.S)
    else: text += '\n\n## Latest newsletter\n\n' + block + '\n'
    path.write_text(text, encoding='utf-8')

def update_index(index: Path, issue_path: Path, issue_date: date):
    data=[]
    if index.exists(): data=json.loads(index.read_text(encoding='utf-8'))
    rec={'date': issue_date.isoformat(), 'path': issue_path.as_posix()}
    data=[r for r in data if r.get('date') != rec['date']] + [rec]
    index.write_text(json.dumps(sorted(data, key=lambda r:r['date'], reverse=True), indent=2)+'\n', encoding='utf-8')

def run(args):
    cfg=load_yaml(args.config); today=date.fromisoformat(args.issue_date) if args.issue_date else date.today()
    papers=load_sample(args.sample_data) if args.sample_data else fetch_arxiv(cfg)
    processed=load_processed(args.processed_file)
    new=dedupe_new(papers, processed)
    reviewed=[(p, openai_review(p,cfg)) for p in new]
    ranked=sorted([(p,r) for p,r in reviewed if r.relevant], key=lambda pr: pr[1].weighted_score, reverse=True)[:cfg['search'].get('paper_limit',12)]
    md=render_newsletter(today, ranked, cfg)
    errors=validate_markdown(md, [p for p,_ in ranked], cfg)
    if errors: raise SystemExit('Validation failed: '+ '; '.join(errors))
    if args.dry_run:
        out=Path(cfg['publication'].get('dry_run_output','newsletters/dry-run-agentic-ai-weekly.md'))
    else:
        out=Path(cfg['publication'].get('output_directory','newsletters')) / str(today.year) / f'{today.isoformat()}-agentic-ai-weekly.md'
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(md, encoding='utf-8')
    if not args.dry_run:
        latest=Path('newsletters/latest.md'); latest.parent.mkdir(exist_ok=True); shutil.copyfile(out, latest)
        update_index(Path('newsletters/index.json'), out, today); update_readme(Path('README.md'), out)
        save_processed(args.processed_file, processed, [p for p,_ in ranked])
    LOG.info('Generated %s with %d papers', out, len(ranked))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config', default='config/newsletter.yml'); ap.add_argument('--processed-file', default='newsletters/processed-papers.json'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--sample-data'); ap.add_argument('--issue-date')
    run(ap.parse_args())
if __name__ == '__main__': main()
