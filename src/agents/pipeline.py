"""Expert agents for the Carbon MoE pipeline."""

from __future__ import annotations

import re
from typing import Any, Protocol

from src.agents.lint import lint_document
from src.agents.synthesizer import synthesize_tsx
from src.schemas.carbon_ui import (
    IntentResult,
    LayoutResult,
    PipelineResult,
    TokenResult,
    WcagResult,
)
from src.utils import allowlist_summary


class SupportsStructured(Protocol):
    model: str

    def structured(self, system: str, user: str, schema: type) -> tuple[Any, Any]:
        ...


SENSITIVE_RE = re.compile(
    r"(ssn|social security|password\s*[:=]|api[_-]?key|secret|yield numbers|confidential)",
    re.I,
)
NEON_RE = re.compile(r"neon\s+green|#[0-9a-fA-F]{6}|hot pink|bright orange", re.I)


def normalize_intent_heuristic(prompt: str) -> IntentResult:
    sensitive = bool(SENSITIVE_RE.search(prompt))
    educational = None
    normalized = prompt
    if NEON_RE.search(prompt):
        educational = (
            "Requested non-Carbon emphasis color. Nearest compliant options: "
            "Primary action $interactive-01 or Danger $support-error."
        )
        normalized = (
            prompt
            + " Use Carbon primary interactive color ($interactive-01) instead of any custom neon/hex color."
        )
    if sensitive:
        normalized = (
            "Build structure only with mock placeholder data. "
            "Do not echo proprietary literals from the user prompt. "
            + normalized
        )
    return IntentResult(
        summary="Generate IBM Carbon UI for the user request",
        primary_components=[],
        needs_responsive=True,
        sensitive_data_detected=sensitive,
        educational_remap=educational,
        mock_data_offered=sensitive,
        normalized_prompt=normalized,
    )


INTENT_SYSTEM = """You are the Intent Normalizer for an IBM Carbon GenUI MoE.
Return JSON matching IntentResult: summary, primary_components (Carbon names only),
needs_responsive, sensitive_data_detected, educational_remap (nullable),
mock_data_offered, normalized_prompt.
If the user asks for non-Carbon colors (e.g. neon green), set educational_remap
explaining nearest Carbon tokens and rewrite normalized_prompt to use them.
If proprietary data appears, set sensitive_data_detected true and rewrite to mock data.
"""

LAYOUT_SYSTEM = """You are the Layout Expert for IBM Carbon.
Emit LayoutResult JSON with document: { id, root } where root is a CarbonNode tree
({ type, props, children }). Use Grid/Column with sm/md/lg props for responsiveness.
Only use allowlisted Carbon components. No hex, px, Tailwind, or inline styles.
"""

TOKEN_SYSTEM = """You are the Token Expert for IBM Carbon.
Given a Carbon JSON tree, bind typography/color/spacing to allowlisted tokens only
(props.token like $heading-03, Tag types, Button kinds). Return TokenResult JSON
with document and tokens_applied list. Strip any illegal styles.
"""

WCAG_SYSTEM = """You are the WCAG Accessibility Expert for IBM Carbon.
Ensure ariaLabel / labelText / titleText exist on interactive regions, preserve focus
behavior for Modal (danger flows), and add accessible names for Tags used as trends.
Return WcagResult JSON with document and aria_notes.
"""


class MoEPipeline:
    def __init__(self, client: SupportsStructured) -> None:
        self.client = client

    def run(self, prompt_id: str, prompt_text: str) -> PipelineResult:
        allow = allowlist_summary()
        intent = normalize_intent_heuristic(prompt_text)
        usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        latency = 0.0

        try:
            intent_llm, u = self.client.structured(
                INTENT_SYSTEM + "\n\n" + allow,
                prompt_text,
                IntentResult,
            )
            intent = intent_llm
            latency += u.latency_seconds
            usage_total["prompt_tokens"] += u.prompt_tokens
            usage_total["completion_tokens"] += u.completion_tokens
            usage_total["total_tokens"] += u.total_tokens
        except Exception:
            pass

        layout, u = self.client.structured(
            LAYOUT_SYSTEM + "\n\n" + allow,
            f"prompt_id={prompt_id}\n{intent.normalized_prompt}",
            LayoutResult,
        )
        latency += u.latency_seconds
        usage_total["prompt_tokens"] += u.prompt_tokens
        usage_total["completion_tokens"] += u.completion_tokens
        usage_total["total_tokens"] += u.total_tokens

        document = layout.document
        document.id = prompt_id

        token, u = self.client.structured(
            TOKEN_SYSTEM + "\n\n" + allow,
            document.model_dump_json(),
            TokenResult,
        )
        latency += u.latency_seconds
        usage_total["prompt_tokens"] += u.prompt_tokens
        usage_total["completion_tokens"] += u.completion_tokens
        usage_total["total_tokens"] += u.total_tokens
        document = token.document
        document.id = prompt_id

        wcag, u = self.client.structured(
            WCAG_SYSTEM + "\n\n" + allow,
            document.model_dump_json(),
            WcagResult,
        )
        latency += u.latency_seconds
        usage_total["prompt_tokens"] += u.prompt_tokens
        usage_total["completion_tokens"] += u.completion_tokens
        usage_total["total_tokens"] += u.total_tokens
        document = wcag.document
        document.id = prompt_id

        lint = lint_document(document)
        if not lint.ok:
            repair_user = (
                document.model_dump_json()
                + "\n\nFix these lint violations:\n"
                + "\n".join(lint.violations)
            )
            token, u = self.client.structured(
                TOKEN_SYSTEM + "\n\n" + allow,
                repair_user,
                TokenResult,
            )
            latency += u.latency_seconds
            usage_total["prompt_tokens"] += u.prompt_tokens
            usage_total["completion_tokens"] += u.completion_tokens
            usage_total["total_tokens"] += u.total_tokens
            document = token.document
            document.id = prompt_id
            lint = lint_document(document)

        tsx = synthesize_tsx(document)
        return PipelineResult(
            prompt_id=prompt_id,
            document=document,
            tsx=tsx,
            intent=intent,
            lint=lint,
            latency_seconds=latency,
            token_usage=usage_total,
            model=getattr(self.client, "model", ""),
        )
