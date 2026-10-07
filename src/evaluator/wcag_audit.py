"""WCAG audit helpers."""

from __future__ import annotations

from typing import Any

from src.schemas.carbon_ui import CarbonDocument, CarbonNode


def _walk(node: CarbonNode, issues: list[str]) -> None:
    props = node.props or {}
    interactive = {
        "Button",
        "TextInput",
        "Search",
        "Dropdown",
        "DatePicker",
        "DatePickerInput",
        "Modal",
        "DataTable",
        "Pagination",
        "Checkbox",
        "Toggle",
    }
    if node.type in interactive:
        has_name = any(
            k in props and props[k]
            for k in (
                "ariaLabel",
                "labelText",
                "titleText",
                "modalHeading",
                "text",
                "legendText",
            )
        )
        if not has_name:
            issues.append(f"missing_accessible_name:{node.type}")
    if node.type == "Tag" and not props.get("ariaLabel") and not props.get("text"):
        issues.append("tag_missing_text")
    if node.type == "Modal":
        if not props.get("modalHeading") and not props.get("ariaLabel"):
            issues.append("modal_missing_heading")
    for child in node.children:
        _walk(child, issues)


def static_wcag_heuristic(document: CarbonDocument) -> dict[str, Any]:
    issues: list[str] = []
    _walk(document.root, issues)
    return {
        "static_violation_count": len(issues),
        "static_issues": issues,
        "note": "Browser axe-core counts come from frontend/playwright; this is a pre-render heuristic.",
    }
