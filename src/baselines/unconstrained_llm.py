"""Unconstrained single-pass baselines (Mistral + GPT-4o)."""

from __future__ import annotations

import json
import time
from typing import Any

from pydantic import BaseModel

from src.llm.clients import MistralClient, OpenAIClient
from src.schemas.carbon_ui import CarbonDocument
from src.utils import allowlist_summary


class BaselineDocument(BaseModel):
    document: CarbonDocument | None = None
    code: str | None = None
    notes: str = ""


BASELINE_SYSTEM = """You are a single-pass UI generator (baseline control).
Given a user request, produce a JSON object with either:
- document: Carbon UI tree { id, root: { type, props, children } } using IBM Carbon names, OR
- code: a React/TSX string using @carbon/react
Prefer returning document when possible.
You are NOT given specialized expert stages—do everything in one shot.
"""


def run_mistral_baseline(prompt_id: str, prompt_text: str) -> dict[str, Any]:
    client = MistralClient()
    t0 = time.perf_counter()
    parsed, usage = client.structured(
        BASELINE_SYSTEM + "\n\n" + allowlist_summary(),
        f"prompt_id={prompt_id}\n{prompt_text}",
        BaselineDocument,
    )
    latency = time.perf_counter() - t0
    return {
        "system": "baseline_mistral",
        "prompt_id": prompt_id,
        "model": usage.model,
        "latency_seconds": latency,
        "token_usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        },
        "document": parsed.document.model_dump() if parsed.document else None,
        "code": parsed.code,
        "raw": usage.raw_text,
    }


def run_gpt4o_baseline(prompt_id: str, prompt_text: str) -> dict[str, Any]:
    client = OpenAIClient()
    t0 = time.perf_counter()
    parsed, usage = client.structured(
        BASELINE_SYSTEM + "\n\n" + allowlist_summary(),
        f"prompt_id={prompt_id}\n{prompt_text}",
        BaselineDocument,
    )
    latency = time.perf_counter() - t0
    return {
        "system": "baseline_gpt4o",
        "prompt_id": prompt_id,
        "model": usage.model,
        "latency_seconds": latency,
        "token_usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        },
        "document": parsed.document.model_dump() if parsed.document else None,
        "code": parsed.code,
        "raw": usage.raw_text,
    }


def save_baseline(result: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
