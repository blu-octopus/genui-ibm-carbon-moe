from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TOKENS_PATH = DATA_DIR / "carbon_tokens.json"
PROMPTS_PATH = DATA_DIR / "prompts" / "prompts.json"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
RESULTS_DIR = DATA_DIR / "results"


@lru_cache(maxsize=1)
def load_carbon_tokens() -> dict:
    with TOKENS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_prompts() -> list[dict]:
    with PROMPTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)["prompts"]


def load_ground_truth(prompt_id: str) -> dict:
    path = GROUND_TRUTH_DIR / f"{prompt_id}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def allowlist_summary() -> str:
    tokens = load_carbon_tokens()
    return (
        "Allowed Carbon components:\n"
        + ", ".join(tokens["components"])
        + "\n\nAllowed color tokens:\n"
        + ", ".join(tokens["colors"])
        + "\n\nAllowed spacing tokens:\n"
        + ", ".join(tokens["spacing"])
        + "\n\nAllowed typography tokens:\n"
        + ", ".join(tokens["typography"])
        + "\n\nResponsive breakpoints: "
        + ", ".join(tokens["breakpoints"])
        + "\n\nNever use hex colors, raw px spacing, Tailwind, or inline style objects."
    )


HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}")
PX_RE = re.compile(r"\b\d+px\b")
RGB_RE = re.compile(r"rgba?\(", re.I)
TAILWIND_RE = re.compile(r"\b(bg|text|flex|rounded|p|m|gap)-\w+")
STYLE_OBJ_RE = re.compile(r"style\s*=\s*\{\{")


def collect_strings(obj: object) -> list[str]:
    found: list[str] = []
    if isinstance(obj, str):
        found.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(collect_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(collect_strings(v))
    return found
