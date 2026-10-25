# biomed-kg-agent

A tool-using LLM agent (LangChain `create_agent`) over a small biomedical knowledge graph
(NetworkX), with CI-gated deterministic tests, a shell data-validation gate, a Docker image
published to GHCR, and a separate LLM evaluation harness (tool selection, answer content,
grounding/hallucination checks).

## Data provenance

`data/triples.csv` is a **hand-curated, illustrative** set of 22 triples, not an extract from a
database. Entries reflect publicly known approved drug-target-indication relationships for
drugs in GSK's therapeutic areas, but they were written by hand, are deliberately incomplete
and simplified, and have not been validated against a primary source. Do not use them for any
clinical or scientific purpose.

One true indication is **held out on purpose**: mepolizumab is approved for EGPA, but the
`Mepolizumab,TREATS,EGPA` edge is omitted so that `repurposing_candidates` can be tested on
whether the graph recovers it via the shared target IL5.

For real data, replace the CSV with a slice of a public biomedical KG (e.g. Hetionet or
PrimeKG) or build triples from Open Targets / ChEMBL. Check each source's licence first.

## Quick start

```bash
bash scripts/validate_data.sh
pip install -e ".[dev]" && ruff check . && pytest -q
export ANTHROPIC_API_KEY=...   # never commit; add as a repo secret for the eval job
python -m kg_agent "Suggest a repurposing hypothesis for mepolizumab"
python eval/run_eval.py
docker build -t kg-agent:local . && bash scripts/smoke.sh
docker run --rm -e ANTHROPIC_API_KEY kg-agent:local "What does niraparib target?"
```

Set `KG_MODEL` (format `provider:model`) to switch models.
