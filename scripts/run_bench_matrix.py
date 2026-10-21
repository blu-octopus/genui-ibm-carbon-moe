"""Run 5 prompts x (baseline allowlist | design.md | MoE) and grade each."""

from __future__ import annotations

import json
import os
import traceback
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

os.environ.setdefault("MISTRAL_MODEL", "mistral-small-latest")

from src.agents.lint import lint_document
from src.agents.pipeline import MoEPipeline
from src.baselines.unconstrained_llm import run_mistral_baseline
from src.evaluator.layout_stability import structural_score
from src.evaluator.token_accuracy import token_compliance, token_compliance_from_text
from src.evaluator.wcag_audit import static_wcag_heuristic
from src.llm.clients import MistralClient
from src.main import _result_path, _write_summary
from src.schemas.carbon_ui import CarbonDocument
from src.utils import load_ground_truth, load_prompts


def grade_payload(payload: dict) -> dict:
    prompt_id = payload["prompt_id"]
    gt = CarbonDocument.model_validate(load_ground_truth(prompt_id))
    if payload.get("document"):
        doc = CarbonDocument.model_validate(payload["document"])
        return {
            "prompt_id": prompt_id,
            "system": payload.get("system"),
            "model": payload.get("model"),
            "context": payload.get("context"),
            "latency_seconds": payload.get("latency_seconds", 0),
            **token_compliance(doc),
            **structural_score(doc, gt),
            **static_wcag_heuristic(doc),
            "lint_ok": lint_document(doc).ok,
        }
    code = payload.get("code") or payload.get("tsx") or payload.get("raw") or ""
    return {
        "prompt_id": prompt_id,
        "system": payload.get("system"),
        "model": payload.get("model"),
        "context": payload.get("context"),
        "latency_seconds": payload.get("latency_seconds", 0),
        **token_compliance_from_text(code),
        "note": "document missing; text-based token compliance only",
    }


def main() -> None:
    rows: list[dict] = []
    client = MistralClient(model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"))
    pipeline = MoEPipeline(client)

    for prompt in load_prompts():
        pid, text = prompt["id"], prompt["text"]
        jobs = [
            ("baseline_allowlist", lambda: run_mistral_baseline(pid, text, context="allowlist")),
            ("baseline_design", lambda: run_mistral_baseline(pid, text, context="design")),
            ("moe", lambda: pipeline.run(pid, text).model_dump() | {"system": "moe_mistral"}),
        ]
        for name, fn in jobs:
            print(f"=== {name} :: {pid} ===", flush=True)
            try:
                result = fn()
                if "system" not in result:
                    result["system"] = name
                path = _result_path(result["system"], pid, result.get("model"))
                path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                print(f"wrote {path}", flush=True)
                row = grade_payload(result)
                rows.append(row)
                print(json.dumps(row, indent=2), flush=True)
            except Exception as exc:
                print(f"FAILED {name} {pid}: {exc}", flush=True)
                traceback.print_exc()
                rows.append(
                    {
                        "prompt_id": pid,
                        "system": name,
                        "error": str(exc),
                    }
                )

    _write_summary(rows, "bench_matrix_mistral")
    print("done", flush=True)


if __name__ == "__main__":
    main()
