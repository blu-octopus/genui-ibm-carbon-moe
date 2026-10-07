"""Structural consistency vs ground-truth JSON + responsive prop checks."""

from __future__ import annotations

from typing import Any

from src.schemas.carbon_ui import CarbonDocument, CarbonNode


def _type_sequence(node: CarbonNode, out: list[str]) -> None:
    out.append(node.type)
    for child in node.children:
        _type_sequence(child, out)


def levenshtein(a: list[str], b: list[str]) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def count_responsive_props(node: CarbonNode) -> int:
    count = 0
    props = node.props or {}
    if node.type == "Column" and any(k in props for k in ("sm", "md", "lg", "xlg", "max")):
        count += 1
    class_name = str(props.get("className", ""))
    if "cds--col-" in class_name:
        count += 1
    for child in node.children:
        count += count_responsive_props(child)
    return count


def structural_score(candidate: CarbonDocument, ground_truth: CarbonDocument) -> dict[str, Any]:
    cand_seq: list[str] = []
    gt_seq: list[str] = []
    _type_sequence(candidate.root, cand_seq)
    _type_sequence(ground_truth.root, gt_seq)
    distance = levenshtein(cand_seq, gt_seq)
    max_len = max(len(cand_seq), len(gt_seq), 1)
    similarity = 1.0 - (distance / max_len)
    cand_resp = count_responsive_props(candidate.root)
    gt_resp = count_responsive_props(ground_truth.root)
    responsive_ok = True if ground_truth.root.type == "Modal" else cand_resp > 0
    return {
        "tree_edit_distance": distance,
        "structure_similarity": round(similarity, 4),
        "candidate_type_count": len(cand_seq),
        "ground_truth_type_count": len(gt_seq),
        "candidate_responsive_nodes": cand_resp,
        "ground_truth_responsive_nodes": gt_resp,
        "responsive_props_present": responsive_ok,
    }
