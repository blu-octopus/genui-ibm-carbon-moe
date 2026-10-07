"""LLM clients: Mistral (MoE) and OpenAI (GPT-4o baseline only)."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    model: str = ""
    raw_text: str = ""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model response: {text[:400]}")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")
    return data


def _sanitize_carbon_node(node: Any) -> dict[str, Any] | None:
    """Drop non-object children / malformed nodes from LLM trees."""
    if not isinstance(node, dict):
        return None
    node_type = node.get("type")
    if not isinstance(node_type, str) or not node_type:
        return None
    props = node.get("props") if isinstance(node.get("props"), dict) else {}
    raw_children = node.get("children", [])
    if not isinstance(raw_children, list):
        raw_children = []
    children: list[dict[str, Any]] = []
    for child in raw_children:
        cleaned = _sanitize_carbon_node(child)
        if cleaned is not None:
            children.append(cleaned)
    return {"type": node_type, "props": props, "children": children}


def _sanitize_document_tree(data: dict[str, Any]) -> dict[str, Any]:
    doc = data.get("document")
    if not isinstance(doc, dict):
        return data
    # Model returned a bare CarbonNode as document
    if "root" not in doc and "type" in doc:
        root = _sanitize_carbon_node(doc)
        if root is not None:
            data = {**data, "document": {"id": str(data.get("id") or "generated"), "root": root}}
        return data
    if "root" in doc:
        root = _sanitize_carbon_node(doc.get("root"))
        if root is not None:
            data = {
                **data,
                "document": {
                    "id": str(doc.get("id") or data.get("id") or "generated"),
                    "root": root,
                },
            }
    return data


def _coerce_schema_payload(data: dict[str, Any], schema: type[BaseModel]) -> dict[str, Any]:
    """Normalize common LLM wrapping mistakes before Pydantic validation."""
    name = schema.__name__
    if set(data.keys()) == {name} and isinstance(data[name], dict):
        data = data[name]

    fields = getattr(schema, "model_fields", {})
    if "document" in fields and "document" not in data and "id" in data and "root" in data:
        extras = {k: v for k, v in data.items() if k not in {"id", "root"}}
        data = {"document": {"id": data["id"], "root": data["root"]}, **extras}
    if "document" in fields:
        data = _sanitize_document_tree(data)
    return data


def _validate_structured(data: dict[str, Any], schema: type[T]) -> T:
    return schema.model_validate(_coerce_schema_payload(data, schema))


class MistralClient:
    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        self.model = model or os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.temperature = temperature
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            from mistralai.client import Mistral

            api_key = (os.getenv("MISTRAL_API_KEY") or "").strip().strip("\"'")
            if not api_key:
                raise RuntimeError("MISTRAL_API_KEY is not set")
            self._client = Mistral(api_key=api_key)
        return self._client

    def complete(self, system: str, user: str) -> LLMUsage:
        client = self._get_client()
        t0 = time.perf_counter()
        resp = client.chat.complete(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        latency = time.perf_counter() - t0
        content = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        return LLMUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage, "total_tokens", 0) or 0,
            latency_seconds=latency,
            model=self.model,
            raw_text=content if isinstance(content, str) else str(content),
        )

    def structured(self, system: str, user: str, schema: type[T]) -> tuple[T, LLMUsage]:
        instruction = (
            "\n\nRespond with a single JSON object whose top-level keys are the schema "
            f"fields for {schema.__name__} (not the class name itself). "
            "CarbonNode children must be arrays of objects with type/props/children only. "
            "No markdown."
        )
        usage = self.complete(system + instruction, user)
        try:
            return _validate_structured(_extract_json(usage.raw_text), schema), usage
        except Exception as first_err:
            retry_user = (
                f"{user}\n\nYour previous JSON failed validation:\n{first_err}\n"
                "Return corrected JSON only."
            )
            usage2 = self.complete(system + instruction, retry_user)
            usage2.prompt_tokens += usage.prompt_tokens
            usage2.completion_tokens += usage.completion_tokens
            usage2.total_tokens += usage.total_tokens
            usage2.latency_seconds += usage.latency_seconds
            return _validate_structured(_extract_json(usage2.raw_text), schema), usage2


class OpenAIClient:
    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        self.model = model or os.getenv("OPENAI_BASELINE_MODEL", "gpt-4o")
        self.temperature = temperature
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def complete(self, system: str, user: str) -> LLMUsage:
        client = self._get_client()
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        latency = time.perf_counter() - t0
        content = resp.choices[0].message.content or ""
        usage = resp.usage
        return LLMUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage, "total_tokens", 0) or 0,
            latency_seconds=latency,
            model=self.model,
            raw_text=content,
        )

    def structured(self, system: str, user: str, schema: type[T]) -> tuple[T, LLMUsage]:
        instruction = (
            "\n\nRespond with a single JSON object whose top-level keys are the schema "
            f"fields for {schema.__name__} (not the class name itself). "
            "CarbonNode children must be arrays of objects with type/props/children only. "
            "No markdown."
        )
        usage = self.complete(system + instruction, user)
        try:
            return _validate_structured(_extract_json(usage.raw_text), schema), usage
        except Exception as first_err:
            retry_user = (
                f"{user}\n\nYour previous JSON failed validation:\n{first_err}\n"
                "Return corrected JSON only."
            )
            usage2 = self.complete(system + instruction, retry_user)
            usage2.prompt_tokens += usage.prompt_tokens
            usage2.completion_tokens += usage.completion_tokens
            usage2.total_tokens += usage.total_tokens
            usage2.latency_seconds += usage.latency_seconds
            return _validate_structured(_extract_json(usage2.raw_text), schema), usage2


@dataclass
class NullClient:
    model: str = "null"
    canned: dict[str, Any] = field(default_factory=dict)

    def structured(self, system: str, user: str, schema: type[T]) -> tuple[T, LLMUsage]:
        return _validate_structured(self.canned, schema), LLMUsage(
            model=self.model, latency_seconds=0.0
        )
