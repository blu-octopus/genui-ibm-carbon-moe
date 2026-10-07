"""Offline unit tests (no API keys required)."""

from __future__ import annotations

from src.agents.lint import lint_document
from src.agents.pipeline import normalize_intent_heuristic
from src.agents.synthesizer import synthesize_tsx
from src.evaluator.layout_stability import structural_score
from src.evaluator.token_accuracy import token_compliance
from src.evaluator.wcag_audit import static_wcag_heuristic
from src.schemas.carbon_ui import CarbonDocument
from src.utils import load_ground_truth, load_prompts


def test_prompts_count():
    assert len(load_prompts()) == 5


def test_ground_truth_loads_and_lints():
    for prompt in load_prompts():
        doc = CarbonDocument.model_validate(load_ground_truth(prompt["id"]))
        lint = lint_document(doc)
        assert lint.ok, (prompt["id"], lint.violations)


def test_token_compliance_high_on_ground_truth():
    for prompt in load_prompts():
        doc = CarbonDocument.model_validate(load_ground_truth(prompt["id"]))
        score = token_compliance(doc)
        assert score["token_compliance_pct"] >= 90.0, (prompt["id"], score)


def test_structure_self_distance_zero():
    for prompt in load_prompts():
        doc = CarbonDocument.model_validate(load_ground_truth(prompt["id"]))
        s = structural_score(doc, doc)
        assert s["tree_edit_distance"] == 0
        assert s["structure_similarity"] == 1.0


def test_synthesizer_emits_carbon_import():
    doc = CarbonDocument.model_validate(load_ground_truth("prompt_05_destructive_modal"))
    tsx = synthesize_tsx(doc)
    assert "@carbon/react" in tsx
    assert "Modal" in tsx


def test_intent_educational_remap():
    intent = normalize_intent_heuristic("Make the CTA neon green and pop more")
    assert intent.educational_remap is not None
    assert "$interactive-01" in intent.normalized_prompt


def test_intent_sensitive_flag():
    intent = normalize_intent_heuristic(
        "Populate the table with confidential Q3 semiconductor yield numbers: 42.1"
    )
    assert intent.sensitive_data_detected is True
    assert intent.mock_data_offered is True


def test_static_wcag_on_form():
    doc = CarbonDocument.model_validate(load_ground_truth("prompt_03_registration_form"))
    result = static_wcag_heuristic(doc)
    assert result["static_violation_count"] == 0
