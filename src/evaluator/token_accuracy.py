"""Token compliance evaluator."""

from __future__ import annotations

import re
from typing import Any

from src.schemas.carbon_ui import CarbonDocument
from src.utils import HEX_RE, PX_RE, RGB_RE, TAILWIND_RE, collect_strings, load_carbon_tokens


def token_compliance(document: CarbonDocument) -> dict[str, Any]:
    tokens = load_carbon_tokens()
    allowed_components = set(tokens["components"])
    allowed_colors = set(tokens["colors"]) | set(tokens.get("cds_css_vars", []))
    allowed_spacing = set(tokens["spacing"])
    allowed_type = set(tokens["typography"])
    allowed_button_kinds = set(tokens.get("button_kinds", []))
    allowed_tag_types = set(tokens.get("tag_types", []))

    valid = 0
    total = 0
    details: list[str] = []

    def walk(node: dict) -> None:
        nonlocal valid, total
        t = node.get("type", "")
        total += 1
        if t in allowed_components:
            valid += 1
        else:
            details.append(f"bad_component:{t}")

        props = node.get("props") or {}
        token = props.get("token")
        if isinstance(token, str) and token.startswith("$"):
            total += 1
            if token in allowed_colors or token in allowed_spacing or token in allowed_type:
                valid += 1
            else:
                details.append(f"bad_token:{token}")

        kind = props.get("kind")
        if isinstance(kind, str) and t == "Button":
            total += 1
            if kind in allowed_button_kinds:
                valid += 1
            else:
                details.append(f"bad_button_kind:{kind}")

        tag_type = props.get("type")
        if isinstance(tag_type, str) and t == "Tag":
            total += 1
            if tag_type in allowed_tag_types:
                valid += 1
            else:
                details.append(f"bad_tag_type:{tag_type}")

        for child in node.get("children") or []:
            walk(child)

    walk(document.root.model_dump())

    blob = " ".join(collect_strings(document.model_dump()))
    for label, cre in (
        ("hex", HEX_RE),
        ("px", PX_RE),
        ("rgb", RGB_RE),
        ("tailwind", TAILWIND_RE),
    ):
        for _ in cre.findall(blob):
            total += 1
            details.append(f"hallucination:{label}")

    pct = (valid / total * 100.0) if total else 0.0
    return {
        "token_compliance_pct": round(pct, 2),
        "valid": valid,
        "total": total,
        "details": details,
    }


def token_compliance_from_text(text: str) -> dict[str, Any]:
    tokens = load_carbon_tokens()
    allowed = set(tokens["components"])
    total = 0
    valid = 0
    details: list[str] = []

    for comp in allowed:
        count = len(re.findall(rf"\b{re.escape(comp)}\b", text))
        if count:
            total += count
            valid += count

    for label, cre in (
        ("hex", HEX_RE),
        ("px", PX_RE),
        ("rgb", RGB_RE),
        ("tailwind", TAILWIND_RE),
    ):
        for _ in cre.findall(text):
            total += 1
            details.append(f"hallucination:{label}")

    if "from '@carbon/react'" in text or 'from "@carbon/react"' in text:
        valid += 1
        total += 1
    else:
        total += 1
        details.append("missing_carbon_import")

    pct = (valid / total * 100.0) if total else 0.0
    return {
        "token_compliance_pct": round(pct, 2),
        "valid": valid,
        "total": total,
        "details": details,
    }
