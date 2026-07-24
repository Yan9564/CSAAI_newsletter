# CSAAI Newsletters

Cloud-based academic newsletter pipeline for CSAAI agentic AI and multi-agent systems coverage.

## Latest newsletter

<!-- latest-newsletter:start -->
Latest newsletter: not generated yet.
<!-- latest-newsletter:end -->

## What the pipeline does

- Runs entirely on GitHub-hosted Ubuntu runners through GitHub Actions.
- Searches arXiv for configurable topics including agentic AI, multi-agent systems, LLM agents, orchestration, coordination, communication, tool-using agents, and enterprise AI agents.
- Retrieves authoritative arXiv metadata: title, authors, abstract, submitted/updated dates, arXiv ID, category, abstract URL, and PDF URL.
- Deduplicates by base arXiv ID using `newsletters/processed-papers.json`.
- Uses the OpenAI API to classify relevance and rank papers, avoiding keyword-only selection.
- Generates Markdown issues under `newsletters/YYYY/YYYY-MM-DD-agentic-ai-weekly.md`, updates `newsletters/latest.md`, `newsletters/index.json`, and this README.
- Validates duplicate papers, missing authors, missing links, malformed Markdown, unsupported numerical statements, and empty output.

## Configuration

Edit `config/newsletter.yml` to adjust:

- `search.topics` and `search.exclusions`
- `search.date_range_days`, `search.max_results_per_topic`, and `search.paper_limit`
- arXiv categories
- publication frequency metadata and output paths
- OpenAI model/retry settings
- validation rules

## GitHub setup

1. In GitHub, open **Settings → Secrets and variables → Actions**.
2. Add repository secret `OPENAI_API_KEY` with an OpenAI API key.
3. Ensure **Settings → Actions → General → Workflow permissions** allows **Read and write permissions** so `GITHUB_TOKEN` can commit generated newsletters.
4. The workflow can run weekly from `.github/workflows/newsletter.yml` or manually through **Actions → Agentic AI Newsletter → Run workflow**.
5. For manual testing, set `dry_run` to `true`; dry runs generate `newsletters/dry-run-agentic-ai-weekly.md` but skip the commit step.

## Local development in the repository workspace

```bash
python -m pip install -e .[dev]
pytest
python -m csaainews.pipeline --dry-run --sample-data config/sample_papers.yml --issue-date 2026-07-24
python scripts/validate_workflow.py
```

The production workflow stores credentials only in the GitHub Actions secret `OPENAI_API_KEY`; no local daemon, database, cron job, external hosting platform, n8n dependency, or self-hosted runner is required.
