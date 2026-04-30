# How to add a verifier

> Status: **stub — fill during WS-8**.

## Programmatic verifier
1. Implement a callable in `verifier/programmatic/<kind>.py` that takes `(agent_output, gold)` and returns `(passed: bool, score: float, details: dict)`.
2. Register it in `verifier/programmatic/__init__.py`.
3. Reference it in a task spec as `verifier: { kind: programmatic, spec: <kind> }`.

## Judge rubric
1. Author `tasks/rubrics/<rubric_id>.yaml` with the schema:
```yaml
id: revenue_report_v1
model: openai:gpt-4o
dimensions:
  - name: factual_accuracy
    weight: 0.4
    description: ...
  - name: use_of_correct_sources
    weight: 0.3
    description: ...
  - name: completeness
    weight: 0.2
    description: ...
  - name: structure
    weight: 0.1
    description: ...
partial_credit: true
output_format: json
```
2. Reference it from a task spec as `verifier: { kind: judge, rubric: revenue_report_v1 }`.
3. Calibrate the rubric: run it against ≥ 3 sample outputs (one obviously good, one mediocre, one bad) and confirm the scores rank correctly.
