# Judge Rubrics

This folder stores rubric YAML files for LLM-as-judge verifiers.

## Current milestone expectation

For the first 10 Meridian Trust tasks, most scoring should stay programmatic.

Add a rubric only when:

1. the answer is open-ended or report-like
2. exact, numeric, or set matching is not enough
3. partial-credit scoring is genuinely needed

Current reference file:

1. `_example_report.yaml`

## Minimal rubric shape

```yaml
id: <unique_rubric_id>
model: openai:gpt-4o
dimensions:
  - name: <dimension_name>
    weight: <0..1>
    description: <what scoring this dimension means>
partial_credit: true
output_format: json
```

## Current limitation

The judge runner is still scaffolded, so rubrics should be added only when the team has a clear downstream plan to wire and test them.
