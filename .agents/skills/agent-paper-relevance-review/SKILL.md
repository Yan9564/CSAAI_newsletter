---
name: agent-paper-relevance-review
description: Reusable CSAAI newsletter workflow skill.
---

## Activation criteria
Use this skill when maintaining the cloud-based CSAAI academic newsletter pipeline and the task touches this skill's responsibilities.

## Procedure
1. Read repository configuration from `config/newsletter.yml`.
2. Prefer reusable Python modules under `csaainews/` instead of embedding long logic here.
3. Run `pytest` after changes.
4. For generated issues, run the pipeline validation stage before publishing.

## Quality requirements
- Use authoritative arXiv metadata and direct arXiv/PDF links.
- Keep configurable topics, exclusions, date ranges, limits and schedule in YAML or workflow inputs.
- Distinguish metadata/abstract evidence from claims requiring full-paper analysis.
- Never invent datasets, sample sizes, benchmarks, results or performance figures.

## Failure handling
- Log actionable errors with the paper ID or stage name.
- Retry transient API failures with backoff.
- Fail closed if validation reports duplicates, missing authors, missing links, malformed Markdown, unsupported numerical statements or empty output.
