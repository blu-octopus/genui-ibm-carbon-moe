"""Deterministic schema + token lint gate."""

from __future__ import annotations

import re

from src.schemas.carbon_ui import CarbonDocument, CarbonNode, LintResult
from src.utils import HEX_RE, PX_RE, RGB_RE, STYLE_OBJ_RE, TAILWIND_RE, collect_strings, load_carbon_tokens


def _walk_types(node: CarbonNode, out: list[str]) -> None:
    out.append(node.type)
    for child in node.children:
        _walk_types(child, out)


def _walk_responsive(node: CarbonNode, found: list[bool]) -> None:
    props = node.props or {}
    if node.type == "Column" and any(k in props for k in ("sm", "md", "lg", "xlg", "max")):
        found.append(True)
    class_name = str(props.get("className", ""))
    if "cds--col-" in class_name:
        found.append(True)
    for child in node.children:
        _walk_responsive(child, found)


def lint_document(document: CarbonDocument) -> LintResult:
    tokens = load_carbon_tokens()
    allowed_components = set(tokens["components"])
    allowed_colors = set(tokens["colors"]) | set(tokens.get("cds_css_vars", []))
    allowed_spacing = set(tokens["spacing"])
    allowed_type = set(tokens["typography"])
    violations: list[str] = []

    types: list[str] = []
    _walk_types(document.root, types)
    for t in types:
        if t not in allowed_components:
            violations.append(f"Unknown or disallowed component: {t}")

    blob = " ".join(collect_strings(document.model_dump()))
    if HEX_RE.search(blob):
        violations.append("Hex color detected (style hallucination)")
    if PX_RE.search(blob):
        violations.append("Raw px length detected (use Carbon spacing tokens)")
    if RGB_RE.search(blob):
        violations.append("rgb/rgba color detected")
    if TAILWIND_RE.search(blob):
        violations.append("Tailwind-like utility class detected")
    if STYLE_OBJ_RE.search(blob):
        violations.append("Inline style object detected")

    for match in re.findall(r"\$[a-z][a-z0-9-]*", blob):
        if (
            match not in allowed_colors
            and match not in allowed_spacing
            and match not in allowed_type
        ):
            violations.append(f"Unknown token reference: {match}")

    responsive: list[bool] = []
    _walk_responsive(document.root, responsive)
    if document.root.type not in {"Modal"} and not responsive:
        violations.append("Missing Carbon responsive Column props (sm/md/lg) or grid classes")

    return LintResult(ok=len(violations) == 0, violations=violations)
