# Judge rubrics

Per-task or shared rubrics for LLM-as-judge verifiers. See `docs/add_a_verifier.md`.

Default model: **`openai:gpt-4o`** (ChatGPT, OpenAI key). Pluggable via the `model` field.

## Rubric schema

```yaml
id: <unique_rubric_id>
model: openai:gpt-4o            # provider:model — pluggable
dimensions:
  - name: <dimension_name>
    weight: <0..1>              # weights sum to 1.0
    description: <what scoring this dimension means>
partial_credit: true
output_format: json
```
