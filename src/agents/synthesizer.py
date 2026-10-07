"""Deterministic Carbon JSON → @carbon/react TSX synthesizer."""

from __future__ import annotations

import json
from typing import Any

from src.schemas.carbon_ui import CarbonDocument, CarbonNode

IMPORTABLE = {
    "Grid",
    "Column",
    "Stack",
    "Button",
    "TextInput",
    "TextArea",
    "Dropdown",
    "DatePicker",
    "DatePickerInput",
    "Tag",
    "Tile",
    "DataTable",
    "Table",
    "TableHead",
    "TableRow",
    "TableHeader",
    "TableBody",
    "TableCell",
    "Pagination",
    "Modal",
    "ModalHeader",
    "ModalBody",
    "ModalFooter",
    "InlineNotification",
    "Tooltip",
    "Form",
    "FormGroup",
    "ProgressIndicator",
    "ProgressStep",
    "Search",
    "Heading",
    "Layer",
}


def _jsx_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, (list, dict)):
        return "{" + json.dumps(value) + "}"
    return "{" + json.dumps(value) + "}"


def _props_to_jsx(props: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in props.items():
        if key in {"text", "children_text"}:
            continue
        if isinstance(value, bool):
            if value:
                parts.append(key)
            else:
                parts.append(f"{key}={{false}}")
        else:
            parts.append(f"{key}={_jsx_value(value)}")
    return (" " + " ".join(parts)) if parts else ""


def _render_node(node: CarbonNode, indent: int = 2) -> str:
    pad = " " * indent
    props = dict(node.props)
    text = props.pop("text", None)
    prop_str = _props_to_jsx(props)

    if node.type == "Heading" and text is not None:
        token = props.get("token", "$body-01")
        class_name = token.replace("$", "").replace("_", "-")
        return f'{pad}<p className="cds--type-{class_name}">{text}</p>'

    if node.type == "Button":
        label = text or "Button"
        return f"{pad}<Button{prop_str}>{label}</Button>"

    if node.type == "Tag":
        label = text or "Tag"
        return f"{pad}<Tag{prop_str}>{label}</Tag>"

    if not node.children and text is None:
        return f"{pad}<{node.type}{prop_str} />"

    inner_parts: list[str] = []
    if text is not None:
        inner_parts.append(f"{pad}  {text}")
    for child in node.children:
        inner_parts.append(_render_node(child, indent + 2))
    inner = "\n".join(inner_parts)
    return f"{pad}<{node.type}{prop_str}>\n{inner}\n{pad}</{node.type}>"


def collect_imports(node: CarbonNode, bag: set[str] | None = None) -> set[str]:
    bag = bag or set()
    if node.type in IMPORTABLE:
        bag.add(node.type)
    for child in node.children:
        collect_imports(child, bag)
    return bag


def synthesize_tsx(document: CarbonDocument, component_name: str | None = None) -> str:
    name = component_name or _to_component_name(document.id)
    imports = sorted(collect_imports(document.root))
    import_line = (
        "import { " + ", ".join(imports) + " } from '@carbon/react';"
        if imports
        else "import '@carbon/react';"
    )
    body = _render_node(document.root, indent=4)
    return (
        f"{import_line}\n"
        "import '@carbon/styles/css/styles.css';\n\n"
        f"export default function {name}() {{\n"
        "  return (\n"
        f"{body}\n"
        "  );\n"
        "}\n"
    )


def _to_component_name(prompt_id: str) -> str:
    parts = [p.capitalize() for p in prompt_id.replace("-", "_").split("_") if p]
    return "".join(parts) or "GeneratedCarbonUI"
