"""CLI entrypoints for MoE runs, baselines, and offline grading."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.agents.lint import lint_document
from src.agents.pipeline import MoEPipeline
from src.agents.synthesizer import synthesize_tsx
from src.baselines.unconstrained_llm import run_gpt4o_baseline, run_mistral_baseline
from src.evaluator.layout_stability import structural_score
from src.evaluator.token_accuracy import token_compliance, token_compliance_from_text
from src.evaluator.wcag_audit import static_wcag_heuristic
from src.llm.clients import MistralClient
from src.schemas.carbon_ui import CarbonDocument
from src.utils import RESULTS_DIR, load_ground_truth, load_prompts


def _ensure_results() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def cmd_synthesize_ground_truth(_: argparse.Namespace) -> None:
    out_dir = Path("data/ground_truth/tsx")
    out_dir.mkdir(parents=True, exist_ok=True)
    for prompt in load_prompts():
        raw = load_ground_truth(prompt["id"])
        doc = CarbonDocument.model_validate(raw)
        tsx = synthesize_tsx(doc)
        path = out_dir / f"{prompt['id']}.tsx"
        path.write_text(tsx, encoding="utf-8")
        print(f"wrote {path}")


def cmd_grade_ground_truth(_: argparse.Namespace) -> None:
    rows = []
    for prompt in load_prompts():
        raw = load_ground_truth(prompt["id"])
        doc = CarbonDocument.model_validate(raw)
        tok = token_compliance(doc)
        struct = structural_score(doc, doc)
        wcag = static_wcag_heuristic(doc)
        lint = lint_document(doc)
        row = {
            "prompt_id": prompt["id"],
            "system": "ground_truth",
            **tok,
            **struct,
            **wcag,
            "lint_ok": lint.ok,
            "lint_violations": ";".join(lint.violations),
        }
        rows.append(row)
        print(json.dumps(row, indent=2))
    _write_summary(rows, "ground_truth_self_grade")


def cmd_run_moe(args: argparse.Namespace) -> None:
    if args.dry_run:
        prompt = next(p for p in load_prompts() if p["id"] == args.prompt_id)
        gt = load_ground_truth(prompt["id"])
        doc = CarbonDocument.model_validate(gt)
        tsx = synthesize_tsx(doc)
        lint = lint_document(doc)
        result = {
            "system": "moe_dry_run",
            "prompt_id": prompt["id"],
            "document": doc.model_dump(),
            "tsx": tsx,
            "lint": lint.model_dump(),
            "latency_seconds": 0.0,
            "token_usage": {},
            "model": "null",
        }
    else:
        pipeline = MoEPipeline(MistralClient())
        prompt = next(p for p in load_prompts() if p["id"] == args.prompt_id)
        out = pipeline.run(prompt["id"], prompt["text"])
        result = out.model_dump()
        result["system"] = "moe_mistral"

    out_path = _ensure_results() / f"{result['system']}_{args.prompt_id}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


def cmd_run_baseline(args: argparse.Namespace) -> None:
    prompt = next(p for p in load_prompts() if p["id"] == args.prompt_id)
    if args.provider == "mistral":
        result = run_mistral_baseline(prompt["id"], prompt["text"])
    else:
        result = run_gpt4o_baseline(prompt["id"], prompt["text"])
    out_path = _ensure_results() / f"{result['system']}_{args.prompt_id}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


def cmd_grade_file(args: argparse.Namespace) -> None:
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    prompt_id = payload.get("prompt_id") or args.prompt_id
    gt = CarbonDocument.model_validate(load_ground_truth(prompt_id))
    rows = []
    if payload.get("document"):
        doc = CarbonDocument.model_validate(payload["document"])
        row = {
            "prompt_id": prompt_id,
            "system": payload.get("system", "unknown"),
            "model": payload.get("model", ""),
            "latency_seconds": payload.get("latency_seconds", 0),
            **token_compliance(doc),
            **structural_score(doc, gt),
            **static_wcag_heuristic(doc),
            "lint_ok": lint_document(doc).ok,
        }
    else:
        code = payload.get("code") or payload.get("tsx") or payload.get("raw") or ""
        row = {
            "prompt_id": prompt_id,
            "system": payload.get("system", "unknown"),
            "model": payload.get("model", ""),
            "latency_seconds": payload.get("latency_seconds", 0),
            **token_compliance_from_text(code),
            "tree_edit_distance": None,
            "structure_similarity": None,
            "responsive_props_present": None,
            **static_wcag_heuristic(gt),
            "note": "document missing; text-based token compliance only",
        }
    rows.append(row)
    print(json.dumps(row, indent=2))
    _write_summary(rows, f"grade_{Path(args.path).stem}")


def _write_summary(rows: list[dict], name: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = _ensure_results() / f"{name}_{stamp}"
    json_path = base.with_suffix(".json")
    csv_path = base.with_suffix(".csv")
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    if rows:
        keys = sorted({k for row in rows for k in row.keys()})
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                flat = {
                    k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                    for k, v in row.items()
                }
                writer.writerow(flat)
    print(f"summary -> {json_path} , {csv_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="genui-moe", description="IBM Carbon Agentic MoE harness")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("synthesize-gt", help="Compile ground-truth JSON to TSX")
    s.set_defaults(func=cmd_synthesize_ground_truth)

    s = sub.add_parser("grade-gt", help="Self-grade ground truth")
    s.set_defaults(func=cmd_grade_ground_truth)

    s = sub.add_parser("run-moe", help="Run MoE pipeline for one prompt")
    s.add_argument("--prompt-id", required=True)
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_run_moe)

    s = sub.add_parser("run-baseline", help="Run unconstrained baseline")
    s.add_argument("--prompt-id", required=True)
    s.add_argument("--provider", choices=["mistral", "gpt4o"], required=True)
    s.set_defaults(func=cmd_run_baseline)

    s = sub.add_parser("grade", help="Grade a saved result JSON against ground truth")
    s.add_argument("--path", required=True)
    s.add_argument("--prompt-id", default=None)
    s.set_defaults(func=cmd_grade_file)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
