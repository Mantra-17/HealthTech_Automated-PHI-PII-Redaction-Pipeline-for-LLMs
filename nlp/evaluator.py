"""
NLPEvaluator — Core evaluation engine for Named Entity Recognition (NER) and PHI redaction.
Calculates Precision, Recall, F1-Score, and support metrics.
Supports exact vs. overlap matching and strict vs. boundary-only type constraints.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, TypedDict, Dict, List, Set, Tuple


class Entity(TypedDict):
    """An entity span representation for evaluation."""
    start: int
    end: int
    type: str
    text: str | None


class MetricResult(TypedDict):
    """Container for precision, recall, and f1 metrics."""
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    support: int


class EvaluationReport(TypedDict):
    """Container for full evaluation metrics including global and per-class breakdowns."""
    global_metrics: MetricResult
    class_metrics: Dict[str, MetricResult]


class NLPEvaluator:
    def __init__(
        self,
        mode: str = "exact",
        strict_type: bool = True,
        aggregation: str = "micro"
    ):
        """
        Initialize the NLP Evaluator.

        Args:
            mode: Matching strategy. Either "exact" (perfect start/end boundaries)
                  or "overlap" (any character overlap).
            strict_type: If True, entities must have matching categories (case-insensitive) to be paired.
            aggregation: Aggregation strategy over multiple documents. Either "micro" or "macro".
        """
        if mode not in ("exact", "overlap"):
            raise ValueError("mode must be either 'exact' or 'overlap'")
        if aggregation not in ("micro", "macro"):
            raise ValueError("aggregation must be either 'micro' or 'macro'")

        self.mode = mode
        self.strict_type = strict_type
        self.aggregation = aggregation

    def overlaps(self, a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
        """Checks if two spans overlap in character space."""
        return a_start < b_end and b_start < a_end

    def compute_iou(self, a_start: int, a_end: int, b_start: int, b_end: int) -> float:
        """Computes Intersection-over-Union (IoU) between two spans."""
        intersection = max(0, min(a_end, b_end) - max(a_start, b_start))
        union = (a_end - a_start) + (b_end - b_start) - intersection
        return intersection / union if union > 0 else 0.0

    def evaluate_single_doc(
        self,
        ground_truth: List[Entity],
        predictions: List[Entity]
    ) -> Tuple[List[Tuple[Entity, Entity, float]], List[Entity], List[Entity]]:
        """
        Evaluates predictions against ground truth for a single document.
        Uses greedy matching based on boundaries and optional types.

        Returns:
            A tuple of (matched_pairs, unmatched_gt, unmatched_pred)
            where matched_pairs is a list of (gt, pred, score) tuples.
        """
        # Ensure input structures are valid
        gt_list = [dict(g) for g in ground_truth]
        pred_list = [dict(p) for p in predictions]

        # Calculate matching scores for all possible pairs
        candidates = []
        for gt_idx, gt in enumerate(gt_list):
            for pred_idx, pred in enumerate(pred_list):
                # 1. Type constraint check
                if self.strict_type:
                    if str(gt.get("type", "")).lower() != str(pred.get("type", "")).lower():
                        continue

                # 2. Boundary constraint check
                matched = False
                score = 0.0
                if self.mode == "exact":
                    if gt["start"] == pred["start"] and gt["end"] == pred["end"]:
                        matched = True
                        score = 1.0
                elif self.mode == "overlap":
                    if self.overlaps(gt["start"], gt["end"], pred["start"], pred["end"]):
                        matched = True
                        score = self.compute_iou(gt["start"], gt["end"], pred["start"], pred["end"])

                if matched:
                    candidates.append((gt_idx, pred_idx, score))

        # Sort candidates: highest score first, then start position
        candidates.sort(
            key=lambda x: (
                -x[2],  # Descending score
                gt_list[x[0]]["start"],
                pred_list[x[1]]["start"]
            )
        )

        matched_gt_indices: Set[int] = set()
        matched_pred_indices: Set[int] = set()
        matched_pairs: List[Tuple[Entity, Entity, float]] = []

        # Greedy match selection
        for gt_idx, pred_idx, score in candidates:
            if gt_idx not in matched_gt_indices and pred_idx not in matched_pred_indices:
                matched_gt_indices.add(gt_idx)
                matched_pred_indices.add(pred_idx)
                matched_pairs.append((gt_list[gt_idx], pred_list[pred_idx], score))

        unmatched_gt = [gt for idx, gt in enumerate(gt_list) if idx not in matched_gt_indices]
        unmatched_pred = [pred for idx, pred in enumerate(pred_list) if idx not in matched_pred_indices]

        return matched_pairs, unmatched_gt, unmatched_pred

    def compute_metrics(self, tp: int, fp: int, fn: int) -> MetricResult:
        """Computes Precision, Recall, and F1 metrics from counts."""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": tp + fn
        }

    def evaluate(
        self,
        ground_truth: Dict[str, List[Entity]] | List[Entity],
        predictions: Dict[str, List[Entity]] | List[Entity]
    ) -> EvaluationReport:
        """
        Evaluates predictions against ground truth across one or multiple documents.

        Args:
            ground_truth: Either a dict mapping doc_id -> list of entities, or a list of entities.
            predictions: Either a dict mapping doc_id -> list of entities, or a list of entities.
        """
        # Standardize format to Dict[str, List[Entity]]
        if isinstance(ground_truth, list):
            gt_docs = {"default_doc": ground_truth}
        else:
            gt_docs = {k: list(v) for k, v in ground_truth.items()}

        if isinstance(predictions, list):
            pred_docs = {"default_doc": predictions}
        else:
            pred_docs = {k: list(v) for k, v in predictions.items()}

        # Align keys
        all_doc_ids = set(gt_docs.keys()).union(pred_docs.keys())

        # Track global statistics
        total_tp = 0
        total_fp = 0
        total_fn = 0

        # Track class-specific counts (global micro aggregation)
        class_tps: Dict[str, int] = {}
        class_fps: Dict[str, int] = {}
        class_fns: Dict[str, int] = {}

        # Track per-document metrics for macro averaging
        doc_precisions: List[float] = []
        doc_recalls: List[float] = []
        doc_f1s: List[float] = []

        for doc_id in all_doc_ids:
            doc_gt = gt_docs.get(doc_id, [])
            doc_pred = pred_docs.get(doc_id, [])

            matched, unmatched_gt, unmatched_pred = self.evaluate_single_doc(doc_gt, doc_pred)

            doc_tp = len(matched)
            doc_fp = len(unmatched_pred)
            doc_fn = len(unmatched_gt)

            total_tp += doc_tp
            total_fp += doc_fp
            total_fn += doc_fn

            # Compute macro list entries
            if doc_gt or doc_pred:
                m = self.compute_metrics(doc_tp, doc_fp, doc_fn)
                doc_precisions.append(m["precision"])
                doc_recalls.append(m["recall"])
                doc_f1s.append(m["f1"])

            # Entity category attribution
            for gt, pred, _ in matched:
                # Group by ground-truth type primarily
                t = str(gt.get("type", "UNKNOWN")).upper()
                class_tps[t] = class_tps.get(t, 0) + 1

            for gt in unmatched_gt:
                t = str(gt.get("type", "UNKNOWN")).upper()
                class_fns[t] = class_fns.get(t, 0) + 1

            for pred in unmatched_pred:
                t = str(pred.get("type", "UNKNOWN")).upper()
                class_fps[t] = class_fps.get(t, 0) + 1

        # Calculate final aggregated global metrics
        if self.aggregation == "macro" and doc_precisions:
            global_metrics: MetricResult = {
                "tp": total_tp,
                "fp": total_fp,
                "fn": total_fn,
                "precision": sum(doc_precisions) / len(doc_precisions),
                "recall": sum(doc_recalls) / len(doc_recalls),
                "f1": sum(doc_f1s) / len(doc_f1s),
                "support": total_tp + total_fn
            }
        else:
            global_metrics = self.compute_metrics(total_tp, total_fp, total_fn)

        # Compute per-class breakdowns
        all_classes = set(class_tps.keys()).union(class_fps.keys()).union(class_fns.keys())
        class_metrics: Dict[str, MetricResult] = {}
        for c in all_classes:
            ctp = class_tps.get(c, 0)
            cfp = class_fps.get(c, 0)
            cfn = class_fns.get(c, 0)
            class_metrics[c] = self.compute_metrics(ctp, cfp, cfn)

        return {
            "global_metrics": global_metrics,
            "class_metrics": class_metrics
        }


def print_ascii_table(report: EvaluationReport, mode: str, strict_type: bool, aggregation: str):
    """Helper to render a clean, human-readable terminal dashboard table."""
    print("\n" + "=" * 80)
    print(f" NLP EVALUATION REPORT  (Mode: {mode.upper()}, Strict Type: {strict_type}, Aggregation: {aggregation.upper()})")
    print("=" * 80)

    # Global Table
    print("\nGLOBAL METRICS:")
    print("-" * 80)
    print(f"{'Metric':<15} | {'TP':<6} | {'FP':<6} | {'FN':<6} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 80)
    gm = report["global_metrics"]
    print(
        f"{'Global Overall':<15} | "
        f"{gm['tp']:<6} | {gm['fp']:<6} | {gm['fn']:<6} | "
        f"{gm['precision']:.2%} | {gm['recall']:.2%} | {gm['f1']:.2%}"
    )
    print("-" * 80)

    # Class Breakdown Table
    if report["class_metrics"]:
        print("\nPER-CATEGORY BREAKDOWN:")
        print("-" * 80)
        print(f"{'Category':<20} | {'TP':<6} | {'FP':<6} | {'FN':<6} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
        print("-" * 80)
        for cat, cm in sorted(report["class_metrics"].items()):
            print(
                f"{cat:<20} | "
                f"{cm['tp']:<6} | {cm['fp']:<6} | {cm['fn']:<6} | "
                f"{cm['precision']:.2%} | {cm['recall']:.2%} | {cm['f1']:.2%}"
            )
        print("-" * 80)
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="NLP Precision and Recall Calculator for Entity/PHI Redaction Results"
    )
    parser.add_argument(
        "--gt",
        required=True,
        help="Path to the Ground Truth JSON file (either flat list or doc_id keyed dict)"
    )
    parser.add_argument(
        "--pred",
        required=True,
        help="Path to the Predictions JSON file (either flat list or doc_id keyed dict)"
    )
    parser.add_argument(
        "--mode",
        choices=["exact", "overlap"],
        default="exact",
        help="Matching mode: exact span match or character overlap match (default: exact)"
    )
    parser.add_argument(
        "--ignore-type",
        action="store_true",
        help="If set, category type matches are ignored during matching evaluation"
    )
    parser.add_argument(
        "--macro",
        action="store_true",
        help="If set, uses macro aggregation over multiple documents instead of micro"
    )

    args = parser.parse_args()

    # Load Ground Truth
    if not os.path.exists(args.gt):
        print(f"Error: Ground truth file '{args.gt}' not found.")
        sys.exit(1)
    with open(args.gt, "r", encoding="utf-8") as f:
        try:
            gt_data = json.load(f)
        except Exception as e:
            print(f"Error: Failed to parse ground truth JSON. Details: {e}")
            sys.exit(1)

    # Load Predictions
    if not os.path.exists(args.pred):
        print(f"Error: Predictions file '{args.pred}' not found.")
        sys.exit(1)
    with open(args.pred, "r", encoding="utf-8") as f:
        try:
            pred_data = json.load(f)
        except Exception as e:
            print(f"Error: Failed to parse predictions JSON. Details: {e}")
            sys.exit(1)

    # Run evaluation
    evaluator = NLPEvaluator(
        mode=args.mode,
        strict_type=not args.ignore_type,
        aggregation="macro" if args.macro else "micro"
    )
    report = evaluator.evaluate(gt_data, pred_data)

    # Print results
    print_ascii_table(
        report,
        mode=args.mode,
        strict_type=not args.ignore_type,
        aggregation="macro" if args.macro else "micro"
    )


if __name__ == "__main__":
    main()
