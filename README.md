![ci](https://github.com/yashbansod123-chemeng/biomed-kg-agent/actions/workflows/ci.yml/badge.svg)

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

## Evaluation

`eval/run_eval.py` runs 5 questions through the agent and scores each answer on three checks:

- `tool_ok`: the expected tool was called.
- `content_ok`: the answer contains the required entities.
- `grounded_ok`: the answer avoids facts that are not in the graph. This is the hallucination check.

A case passes only if all three checks pass.

**Model:** `<KG_MODEL used, e.g. anthropic:claude-haiku-5-5>` · **Runs:** 3

| Question | Tools called | Result |
|---|---|---|
| Which drugs treat asthma, including subtypes? | `drugs_for_disease` | 3/3 pass |
| What does niraparib target? | `targets_of_drug` | 3/3 pass |
| Suggest a repurposing hypothesis for mepolizumab | `repurposing_candidates`, `targets_of_drug` | 3/3 pass |
| How is mepolizumab connected to EGPA? | `connection_path`, `drugs_for_disease` | 3/3 pass |
| What does aspirin target? (not in graph) | `targets_of_drug` ×2 | 3/3 pass |

**Pass rate: 100% in each of 3 runs (15/15 case-runs).**

### Observations

- **Held-out indication recovered.** The `Mepolizumab → EGPA` edge is deliberately absent from the data. The agent proposed EGPA as a repurposing hypothesis via the shared target IL5 and cited the supporting triples.
- **Grounding held for an out-of-graph drug.** Aspirin is not in the graph. The agent reported that it could not find aspirin rather than answering from the model's own knowledge of cyclooxygenase. It called the lookup tool twice before concluding.
- **The agent called more tools than strictly required.** In two cases it made a second verification call, for example checking whether mepolizumab already treats EGPA. This costs extra tokens but did not change correctness.
- **Prompt ablation.** Removing the "never answer from your own memory" instruction from the system prompt gave: `<result of the Step 9 experiment>`.

### Limitations

- **Small sample.** With 0 failures in 15 case-runs, the rule of three puts the 95% upper bound on the per-case failure rate at about 20%. Repeated runs of the same question are correlated, so the true uncertainty is wider than that. A 100% pass rate here shows the design works; it does not establish robustness.
- **Lenient scoring.** Substring matching cannot catch a wrong statement that happens to mention the right entity. A larger, adversarial case set or an LLM-as-judge rubric would be the next step.
- **Illustrative data.** The graph has 22 hand-curated triples; see Data provenance above.
- **Manual evaluation only.** The evaluation runs on manual trigger (`workflow_dispatch`), not on every push, because it costs money and gives a stochastic result. Deterministic tests gate every change.