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
    return json.loads(text[start : end + 1])


class MistralClient:
    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        self.model = model or os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.temperature = temperature
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            from mistralai import Mistral

            api_key = os.getenv("MISTRAL_API_KEY")
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
        usage = self.complete(
            system
            + "\n\nRespond with a single JSON object that matches the required schema. No markdown.",
            user,
        )
        data = _extract_json(usage.raw_text)
        return schema.model_validate(data), usage


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
        usage = self.complete(
            system
            + "\n\nRespond with a single JSON object that matches the required schema. No markdown.",
            user,
        )
        data = _extract_json(usage.raw_text)
        return schema.model_validate(data), usage


@dataclass
class NullClient:
    model: str = "null"
    canned: dict[str, Any] = field(default_factory=dict)

    def structured(self, system: str, user: str, schema: type[T]) -> tuple[T, LLMUsage]:
        return schema.model_validate(self.canned), LLMUsage(model=self.model, latency_seconds=0.0)
