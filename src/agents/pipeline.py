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

FEW_SHOT_LAYOUT = """
Scope: ONLY DOM hierarchy + responsive Grid/Column props. Do NOT invent hex/px/Tailwind.
Do NOT finish token binding or aria work—leave placeholders for later experts.

Example good skeleton:
{
  "document": {
    "id": "example",
    "root": {
      "type": "Grid",
      "props": {"fullWidth": true},
      "children": [
        {"type": "Column", "props": {"sm": 4, "md": 4, "lg": 4}, "children": [
          {"type": "Tile", "props": {}, "children": []}
        ]},
        {"type": "Column", "props": {"sm": 4, "md": 4, "lg": 4}, "children": [
          {"type": "Tile", "props": {}, "children": []}
        ]},
        {"type": "Column", "props": {"sm": 4, "md": 4, "lg": 4}, "children": [
          {"type": "Tile", "props": {}, "children": []}
        ]},
        {"type": "Column", "props": {"sm": 4, "md": 4, "lg": 4}, "children": [
          {"type": "Tile", "props": {}, "children": []}
        ]}
      ]
    }
  }
}
"""

FEW_SHOT_TOKEN = """
Scope: ONLY Carbon component choice + token-ish props (kind, type, token, gap).
Strip illegal styles. Do NOT redesign the grid.

Bad vibe-coded leaf:
{"type":"Button","props":{"style":{"backgroundColor":"#0f62fe","padding":"10px"},"text":"Save"},"children":[]}

Good token-bound leaf:
{"type":"Button","props":{"kind":"primary","text":"Save"},"children":[]}

Bad status:
{"type":"Heading","props":{"text":"Active","style":{"color":"#24a148"}},"children":[]}

Good status:
{"type":"Tag","props":{"type":"green","text":"Active"},"children":[]}

Typography: use props.token like "$heading-03" or "$label-01" on Heading nodes.
"""

FEW_SHOT_WCAG = """
Scope: ONLY accessibility attributes and accessible names.
Add/fix labelText, ariaLabel, titleText, modalHeading, table ariaLabel.
Do NOT change layout structure or invent hex colors.
Ensure interactive nodes are named; Modal danger flows keep clear primary/secondary labels.
"""


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

LAYOUT_SYSTEM = f"""You are the Layout Expert for IBM Carbon.
Emit LayoutResult JSON with document: {{ id, root }} where root is a CarbonNode tree
({{ type, props, children }}). Use Grid/Column with sm/md/lg props for responsiveness.
Only use allowlisted Carbon components. No hex, px, Tailwind, or inline styles.
{FEW_SHOT_LAYOUT}
"""

TOKEN_SYSTEM = f"""You are the Token Expert for IBM Carbon.
Given a Carbon JSON tree, bind typography/color/spacing to allowlisted tokens only
(props.token like $heading-03, Tag types, Button kinds). Return TokenResult JSON
with document and tokens_applied list. Strip any illegal styles.
{FEW_SHOT_TOKEN}
"""

WCAG_SYSTEM = f"""You are the WCAG Accessibility Expert for IBM Carbon.
Ensure ariaLabel / labelText / titleText exist on interactive regions, preserve focus
behavior for Modal (danger flows), and add accessible names for Tags used as trends.
Return WcagResult JSON with document and aria_notes.
{FEW_SHOT_WCAG}
"""


class MoEPipeline:
    def __init__(self, client: SupportsStructured, max_lint_retries: int = 2) -> None:
        self.client = client
        self.max_lint_retries = max_lint_retries

    def run(self, prompt_id: str, prompt_text: str) -> PipelineResult:
        allow = allowlist_summary()
        intent = normalize_intent_heuristic(prompt_text)
        usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        latency = 0.0

        def _acc(u: Any) -> None:
            nonlocal latency
            latency += u.latency_seconds
            usage_total["prompt_tokens"] += u.prompt_tokens
            usage_total["completion_tokens"] += u.completion_tokens
            usage_total["total_tokens"] += u.total_tokens

        try:
            intent_llm, u = self.client.structured(
                INTENT_SYSTEM + "\n\n" + allow,
                prompt_text,
                IntentResult,
            )
            intent = intent_llm
            _acc(u)
        except Exception:
            pass

        layout, u = self.client.structured(
            LAYOUT_SYSTEM + "\n\n" + allow,
            f"prompt_id={prompt_id}\n{intent.normalized_prompt}",
            LayoutResult,
        )
        _acc(u)

        document = layout.document
        document.id = prompt_id

        token, u = self.client.structured(
            TOKEN_SYSTEM + "\n\n" + allow,
            document.model_dump_json(),
            TokenResult,
        )
        _acc(u)
        document = token.document
        document.id = prompt_id

        wcag, u = self.client.structured(
            WCAG_SYSTEM + "\n\n" + allow,
            document.model_dump_json(),
            WcagResult,
        )
        _acc(u)
        document = wcag.document
        document.id = prompt_id

        lint = lint_document(document)
        retries = 0
        while not lint.ok and retries < self.max_lint_retries:
            retries += 1
            repair_user = (
                document.model_dump_json()
                + "\n\nValidation Error — fix EVERY listed violation using only Carbon tokens/components.\n"
                + "\n".join(f"- {v}" for v in lint.violations)
                + "\nReturn TokenResult JSON with the corrected document."
            )
            token, u = self.client.structured(
                TOKEN_SYSTEM + "\n\n" + allow,
                repair_user,
                TokenResult,
            )
            _acc(u)
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
