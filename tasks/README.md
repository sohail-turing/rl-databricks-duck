# Tasks

100 task specs (`T-001.yaml` … `T-100.yaml`). Schema in `validator.md` §7.

Distribution target:
- `T-001` … `T-010` — easy (Pass@5 > 80%)
- `T-011` … `T-030` — medium (20% < Pass@5 ≤ 80%)
- `T-031` … `T-100` — hard (Pass@5 < 20%)

`tasks/_template.yaml` is the starter template — copy it for new tasks.
`tasks/_example.yaml` is a fully fleshed reference so the team has a north star.
`tasks/rubrics/` holds LLM-as-judge rubrics referenced by task specs.

See `docs/add_a_task.md` for the authoring loop.
