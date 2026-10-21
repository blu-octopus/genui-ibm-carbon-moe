"""Unconstrained single-pass baselines (Mistral + GPT-4o), optional design.md saturation."""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from pydantic import BaseModel

from src.llm.clients import MistralClient, OpenAIClient
from src.schemas.carbon_ui import CarbonDocument
from src.utils import ROOT, allowlist_summary

ContextMode = Literal["none", "allowlist", "design"]


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


def load_design_md() -> str:
    path = ROOT / "data" / "design.md"
    return path.read_text(encoding="utf-8")


def _user_message(prompt_id: str, prompt_text: str, context: ContextMode) -> str:
    parts: list[str] = []
    if context == "design":
        parts.append(load_design_md())
        parts.append("\n\n---\nEND DESIGN CONTEXT. Follow it strictly.\n---\n")
    elif context == "allowlist":
        parts.append(allowlist_summary())
        parts.append("\n")
    parts.append(f"prompt_id={prompt_id}\n{prompt_text}")
    return "".join(parts)


def _system_for_context(context: ContextMode) -> str:
    if context == "design":
        return BASELINE_SYSTEM + "\nDesign rules are in the user message. Obey them."
    if context == "allowlist":
        return BASELINE_SYSTEM + "\n\n" + allowlist_summary()
    return BASELINE_SYSTEM


def run_mistral_baseline(
    prompt_id: str,
    prompt_text: str,
    context: ContextMode = "allowlist",
) -> dict[str, Any]:
    client = MistralClient()
    t0 = time.perf_counter()
    parsed, usage = client.structured(
        _system_for_context(context),
        _user_message(prompt_id, prompt_text, context),
        BaselineDocument,
    )
    latency = time.perf_counter() - t0
    system = "baseline_mistral_design_md" if context == "design" else "baseline_mistral"
    return {
        "system": system,
        "context": context,
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


def run_gpt4o_baseline(
    prompt_id: str,
    prompt_text: str,
    context: ContextMode = "allowlist",
) -> dict[str, Any]:
    client = OpenAIClient()
    t0 = time.perf_counter()
    parsed, usage = client.structured(
        _system_for_context(context),
        _user_message(prompt_id, prompt_text, context),
        BaselineDocument,
    )
    latency = time.perf_counter() - t0
    system = "baseline_gpt4o_design_md" if context == "design" else "baseline_gpt4o"
    return {
        "system": system,
        "context": context,
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
