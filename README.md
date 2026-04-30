# Databricks RL Environment Build

Realistic, production-like Databricks workspace + 100-task analytical evaluation suite + verifier/harness, built for Databricks by Turing.

## Start here

1. [`context.md`](./context.md) — what we're building, vocabulary, taxonomies, principles.
2. [`plan.md`](./plan.md) — 6-week execution plan, workstreams, locked decisions, risks.
3. [`validator.md`](./validator.md) — 4-layer validation strategy and the Fisher's-exact ablation method.

## Source documents (input)

- [`reference_docs/`](./reference_docs) — the three source docs this build is derived from:
  - `Workspace taxonomies and verification.docx` (Databricks methodology)
  - `How Agents Distinguish Tables_ Concrete Examples for Workspace Complexity.docx` (Databricks recipe)
  - `[Databricks __ Turing] - Initial Proposal Databricks RL Env Build-v0.docx` (Turing engagement scope)

## Repo layout

| Path                    | What lives here                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| `docs/`                 | Detail design docs (domain model, catalog layout, naming conventions, runbooks).               |
| `workspace/manifests/`  | YAML manifests of every table / notebook / dashboard / Drive doc, with taxonomy tags.          |
| `workspace/generators/` | Python generators that produce the synthetic data.                                              |
| `workspace/notebooks/`  | Source notebooks that get loaded into the workspace.                                            |
| `workspace/dashboards/` | Dashboard definitions (JSON / YAML).                                                            |
| `workspace/drive/`      | Source documents that get uploaded to Google Drive (interview notes, briefs, memos).            |
| `tasks/`                | Task specs (`T-001.yaml` … `T-100.yaml`). Schema in `validator.md` §7.                          |
| `tasks/rubrics/`        | LLM-as-judge rubrics (per-task or shared).                                                      |
| `verifier/programmatic/`| Programmatic verifier kernel (exact, set, numeric, frame).                                      |
| `verifier/judge/`       | Judge runner. Default model: ChatGPT (OpenAI). Pluggable.                                        |
| `harness/`              | Run harness, tool surface, ablation apply/undo scripts, session manager.                        |
| `verification/`         | Raw runs of the baseline agent + per-claim Fisher's-exact reports.                              |
| `tools/`                | Utility scripts (coverage matrix generator, stats helpers).                                     |

## Quick start (after access lands)

```bash
# Install deps (Python 3.11)
pip install -r requirements.txt

# Run the harness against a single task
python -m harness.runner --task T-001 --run-id local-001

# Generate the coverage matrix
python tools/coverage_matrix.py
```

## Status

**Currently in WS-0 (offline-buildable path).** Workspace + Drive + MCP credentials are still being procured. See [`plan.md`](./plan.md) §2.1 for the parallel offline workstream.
