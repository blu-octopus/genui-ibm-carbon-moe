"""Pydantic schemas for IBM Carbon UI trees (governed IR)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ComponentType = Literal[
    "Grid",
    "Column",
    "Stack",
    "FlexGrid",
    "Row",
    "Button",
    "TextInput",
    "TextArea",
    "Dropdown",
    "DatePicker",
    "DatePickerInput",
    "Checkbox",
    "RadioButton",
    "RadioButtonGroup",
    "Toggle",
    "Tag",
    "Tile",
    "ClickableTile",
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
    "ToastNotification",
    "Tooltip",
    "Form",
    "FormGroup",
    "FormLabel",
    "ProgressIndicator",
    "ProgressStep",
    "NumberInput",
    "Select",
    "SelectItem",
    "Search",
    "Link",
    "Heading",
    "Section",
    "Layer",
]


class CarbonNode(BaseModel):
    type: str = Field(..., description="IBM Carbon component name")
    props: dict[str, Any] = Field(default_factory=dict)
    children: list[CarbonNode] = Field(default_factory=list)


class CarbonDocument(BaseModel):
    id: str
    root: CarbonNode


class IntentResult(BaseModel):
    summary: str
    primary_components: list[str]
    needs_responsive: bool = True
    sensitive_data_detected: bool = False
    educational_remap: str | None = None
    mock_data_offered: bool = False
    normalized_prompt: str


class LayoutResult(BaseModel):
    document: CarbonDocument


class TokenResult(BaseModel):
    document: CarbonDocument
    tokens_applied: list[str] = Field(default_factory=list)


class WcagResult(BaseModel):
    document: CarbonDocument
    aria_notes: list[str] = Field(default_factory=list)


class LintResult(BaseModel):
    ok: bool
    violations: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    prompt_id: str
    document: CarbonDocument
    tsx: str
    intent: IntentResult | None = None
    lint: LintResult | None = None
    latency_seconds: float = 0.0
    token_usage: dict[str, int] = Field(default_factory=dict)
    model: str = ""


CarbonNode.model_rebuild()
