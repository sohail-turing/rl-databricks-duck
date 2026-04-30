# Verifier

Two kernels:

- `programmatic/` — exact / set / numeric / frame match. Workspace-agnostic. Buildable in WS-0.
- `judge/` — LLM-as-judge runner. Pluggable model. Default ChatGPT (OpenAI). Buildable in WS-0.

Both kernels return a `VerifierResult`:

```python
@dataclass
class VerifierResult:
    passed: bool
    score: float       # 0.0 to 1.0
    details: dict      # per-dimension breakdown for judge; comparison details for programmatic
```
