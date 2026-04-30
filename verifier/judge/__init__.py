"""LLM-as-judge runner.

Default model: ChatGPT (OpenAI). Pluggable per-rubric via the `model` field
(`openai:gpt-4o`, `anthropic:claude-3-5-sonnet`, ...).

Stub: full implementation in WS-8.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .. import VerifierResult


DEFAULT_MODEL = os.environ.get("JUDGE_DEFAULT_MODEL", "openai:gpt-4o")


@dataclass
class Rubric:
    id: str
    model: str
    dimensions: list[dict]
    partial_credit: bool = True
    output_format: str = "json"


def load_rubric(rubric_id: str, rubric_dir: str = "tasks/rubrics") -> Rubric:
    raise NotImplementedError("WS-8 stub: load Rubric YAML from disk and validate against schema.")


def run_judge(rubric: Rubric, agent_output: str, task_context: dict) -> VerifierResult:
    raise NotImplementedError(
        "WS-8 stub: dispatch to provider client by `rubric.model` prefix "
        "(openai: -> openai client; anthropic: -> anthropic client) and score."
    )
