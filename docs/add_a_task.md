# How to add a task

> Status: **stub — fill during WS-7**.

1. Pick a `T-XXX` ID. Add `tasks/T-XXX.yaml` following the schema in `validator.md` §7.
2. Fill in `domain`, `sub_domain`, `difficulty`, `query`, `expected_assets`, `gold_sql`, `gold_answer`, `verifier`.
3. List candidate `distractors` with `taxonomy_id` from `validator.md` §2.1. Set `verified: false`.
4. List candidate `anchors` with `taxonomy_id` from `validator.md` §2.2. Set `verified: false`.
5. For hard tasks, write a `minimal_hint`.
6. Dry-run the gold solution against the harness to confirm the verifier scores it correctly.
7. Submit for verification (WS-9). Each claim runs the Fisher's-exact protocol; verified claims have their `verified` flag flipped to `true`.
8. Re-run `tools/coverage_matrix.py` to confirm coverage hasn't regressed.

## Common pitfalls

- **Claiming a distractor that doesn't actually distract.** The Fisher's-exact bar will reject it (p ≥ 0.05 or OR < 3). Either rewrite the distractor or drop it.
- **Hard tasks where un-hinted Pass@5 is 0.** Use the minimal-hint pathway. The hint must contain only knowledge an agent could plausibly infer from the workspace + general world knowledge.
- **Two anchors that overlap completely.** Each anchor needs its own statistical justification; if removing one is fully redundant with removing the other, only one is verifiable.
