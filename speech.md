# Team Discussion Script — Shared Plan

> **TL;DR (paste into meeting invite):** 30-min sync to lock the strategy in `shared_plan.md` before we start execution. We’re delivering a Databricks RL evaluation environment in **6 weeks** as **5 vertical slices** (Inc-0 to Inc-5) — workspace + tasks + verifier shipped together each increment, not waterfall. The 1000+ tables are **accumulated incrementally** with a per-day cap of ~100 (not generated in one shot). I need your input on: (1) comfort with the 6-week + Inc-0→Inc-5 model, (2) any blockers for workspace/MCP access by Day 6, (3) whether the per-day table cap and Inc-0 hard gate (5 tasks + 1 mini-verification by Day 10) are realistic. Pre-read: `shared_plan.md` §5.3, §7, §8.4, §11.

---

Hey everyone, thanks for joining.

I want to walk through the strategy in `shared_plan.md` so we’re aligned before we start execution. I’ve restructured a few things since the first draft based on feedback from the lead and from you, so I’ll flag those changes as I go.

The goal is simple: in **6 weeks**, we deliver a realistic Databricks RL evaluation environment — workspace, tasks, and verification harness — not just data assets in isolation.

The foundational design decision is the **common entity pool** in `main.certified.*`. We generate and lock shared entities first (`customers`, `organisations`, `products`, `employees`, `financial_periods`, `currencies`, `fx_rates`, `cost_centers`, `geographies`), then build domain tables on top. That gives us consistent joins across Sales, Marketing, Finance, and Engineering, and avoids downstream rework. This is non-negotiable — without it, tasks become trivial or impossible.

---

### How we’re delivering it: incremental vertical slices, not waterfall

The biggest change from the first draft is that we are **not** going to "build the workspace, then author tasks, then verify at the end." That model is too risky — we'd discover task-authoring or verifier problems in Week 5, with no time to recover.

Instead, after a Week 1 offline foundation, work goes in **vertical slices**. Each increment (Inc-0 through Inc-5) delivers workspace + tasks + verifier + mini-verification together, end-to-end.

At a high level:

- **Week 1 — Foundation (offline).** Generators, harness, agent tool surface, all on DuckDB. No dependency on workspace access.
- **Week 2 — Inc-0: Sales-only slice.** Pool + Sales orders sub-domain + ~15 notebooks + ~15 dashboards + 5 tasks (3 easy + 2 medium) + 1 N=10 mini-verification. By Friday we have a working slice that can be demoed.
- **Week 3 — Inc-1: + Marketing.** Adds Sales accts/pipeline + Marketing campaigns; cumulative 15 tasks; first cross-domain task; N=10 on 2 claims.
- **Week 4 — Inc-2 + Inc-3: + Finance + Engineering.** Workspace gold/distractor surface complete; 45 tasks; **Phase 1 walkthrough with Databricks on Day 20.** M1 review window opens.
- **Week 5 — Inc-4: hard task sprint.** Remaining 55 hard tasks + ablation scripts + minimal-hint authoring. Background table pool batched on Day 23. M1 sign-off mid-week.
- **Week 6 — Inc-5: full verification + Phase 2.** N=30 verification across all 100 tasks + triage + re-runs + joint walkthrough Day 30.

By end of **Week 2** we already have something working. Every week after adds a domain on top of a known-good slice. This is in §7 of the doc.

---

### About the “1000+ tables” — we are not generating them in one shot

I want to flag this upfront because I know it’s been a concern. The 1000+ table figure is the **end-state** target, accumulated over the program. We are **not** lift-and-shifting 1000 tables in Week 2.

Three buckets, three different schedules (this is in §5.3):

- **Gold tables (~150)** — referenced by ≥ 1 task. Generated on-demand inside the increment that authors that task. Each table’s existence is justified by a task.
- **Distractor cluster (~400)** — 3–5 distractors per gold table per the `validator.md` taxonomy. Generated alongside their gold table — never ships separately.
- **Background pool (~500)** — pure search-space inflation; not referenced by any task. **Batched once in Week 5 (Day 23)** after the pattern is validated against ~400 tables of real task usage.

**Per-day cap is ~100 new tables.** Inc-0 ends Day 10 with ~50 tables — pool plus Sales orders sub-domain. If the schema or noise pattern is wrong, we throw away 50 tables, not 1000. The only big-batch day is Day 23, when the pattern is already proven on 400 tables of live usage.

Five rules in §5.3 protect the team here:

1. No more than ~100 new tables per day.
2. Each task declares the tables it needs; generators only emit those.
3. Pattern is validated on the first ~30 tables (Inc-0). Throw away 30 if wrong, not 1000.
4. Background pool is the last batch, not the first.
5. Generators are templated and parameterized — same code emits 1 table or 1000.

---

### Quality bar — distractors/anchors must be statistically verified

Distractors and anchors are not assumed — they have to be statistically verified via ablation. The protocol is in `validator.md` §5.

Two layers of verification in our plan:

- **Mini-verification (N=10) at the end of each increment** — 1–5 claims, runs in minutes, costs ~$2–3 per increment. This is a **pipeline check**, not the ship bar. It catches ablation/scoring/agent regressions early so we don’t discover them at scale in Week 6.
- **Full N=30 verification in Week 6** — every claim, Fisher’s exact at α=0.05, OR ≥ 3. This is the ship bar from `validator.md` §5.3. About 30,000 baseline-agent runs total, ~$1.5–3k in API cost, ~16.5 hours of wall time at 30-way parallelism.

Mini-verification does **not** replace the N=30 final bar — it just lets us catch problems in Week 2 instead of Week 6.

---

### I need your input on three things today

- Are we comfortable with the 6-week timeline and the Inc-0 → Inc-5 incremental delivery model?
- Any technical blockers we already know for workspace, Drive, or MCP access landing by Week 2 / Day 6? (Week 1 is fully offline on DuckDB regardless, so we’re covered up to that point.)
- Any gaps in risks or dependencies we should add before we lock execution? In particular: does the **~100 tables/day cap** feel realistic to whoever owns the generators, and is the **Inc-0 hard gate** (5 working tasks + 1 mini-verification by Day 10) achievable?

If we align on these now, we can freeze this as the working strategy and start execution.

Thanks — open for feedback.

---

## FAQ — questions that have already come up

### What does `N=30` mean?

`N=30` means for each distractor/anchor verification check, we run the baseline agent **30 times with the asset present** and **30 times with it removed/hidden**. Then we compare pass/fail outcomes statistically (Fisher’s exact + odds ratio). This gives enough evidence that a distractor or anchor is actually affecting agent performance, instead of relying on one-off runs.

Per claim that’s 60 runs. Across 100 tasks × ~5 claims/task that's ~30,000 baseline-agent runs in Week 6.

### What does N=10 mini-verification mean, and how is it different?

Mini-verification runs the same A/B test as N=30, but only 10 runs per condition (20 total per claim). It’s **cheap** (~$3 per increment) and **fast** (minutes). The point is to validate the **pipeline** end-to-end — does the ablation script work, does the agent see the change, does the scorer behave? — **not** to declare a claim verified.

A claim is only ever called "verified" after passing the full N=30 bar in Week 6.

### Why not drop N to 12?

Totally fair to ask — the runtime is real. But N=12 isn’t really a smaller version of the same test; it ends up being a different test.

Our methodology in `validator.md` §5 verifies **each distractor and each anchor as its own claim**, with its own ablation, and asks Fisher’s exact whether removing it actually moved the needle (`α = 0.05`, `OR ≥ 3`). At ~3 runs per cell you basically can’t reach that bar even when the effect is real — you’d need a near-perfect on/off swing every time, and most real distractors don’t behave that cleanly. So we'd end up rejecting claims that actually work, just because the test is underpowered.

There’s also a coverage angle: Phase 2 acceptance is gated on every taxonomy element being covered by at least one **verified** claim (`validator.md` §6). A pooled "with both / without both" design doesn’t verify the individual claims — it tells us the bundle hurt or helped on average, which doesn’t fill that matrix.

That said, I don’t want to be precious about N=30 if compute is the real concern. The doc already allows **N=20** on easy claims with obviously large effects (`validator.md` §5.3), and we can tier N by difficulty (e.g. 20 / 25 / 30) to claw back roughly a third of the runtime without touching the acceptance bar. So if the worry is "30 × everything is too much," let’s talk about tiering rather than dropping to 12 across the board.
