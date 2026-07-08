"""
Unit tests for the NLP evaluation engine (``nlp/evaluator.py``).
"""

from __future__ import annotations

import pytest
from nlp.evaluator import NLPEvaluator, Entity

# Repeated test value organized into a constant for maintainability
JOHN_SMITH_ENTITY = {"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}


def test_exact_match_basic():
    evaluator = NLPEvaluator(mode="exact", strict_type=True)
    gt = [JOHN_SMITH_ENTITY]
    pred = [JOHN_SMITH_ENTITY]
    
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 1, f"Expected 1 True Positive, got {gm['tp']}"
    assert gm["fp"] == 0, f"Expected 0 False Positives, got {gm['fp']}"
    assert gm["fn"] == 0, f"Expected 0 False Negatives, got {gm['fn']}"
    assert gm["precision"] == 1.0, f"Expected precision 1.0, got {gm['precision']}"
    assert gm["recall"] == 1.0, f"Expected recall 1.0, got {gm['recall']}"
    assert gm["f1"] == 1.0, f"Expected F1 1.0, got {gm['f1']}"
    assert gm["support"] == 1, f"Expected support 1, got {gm['support']}"


def test_exact_match_type_strictness():
    # When strict_type is True, type mismatch should prevent match
    evaluator = NLPEvaluator(mode="exact", strict_type=True)
    gt = [JOHN_SMITH_ENTITY]
    pred = [{"start": 0, "end": 10, "type": "DATE", "text": "John Smith"}]
    
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 0
    assert gm["fp"] == 1
    assert gm["fn"] == 1
    assert gm["precision"] == 0.0
    assert gm["recall"] == 0.0
    assert gm["f1"] == 0.0

    # When strict_type is False, type mismatch is ignored
    evaluator_lenient = NLPEvaluator(mode="exact", strict_type=False)
    report_lenient = evaluator_lenient.evaluate(gt, pred)
    gm_lenient = report_lenient["global_metrics"]
    
    assert gm_lenient["tp"] == 1
    assert gm_lenient["fp"] == 0
    assert gm_lenient["fn"] == 0
    assert gm_lenient["precision"] == 1.0
    assert gm_lenient["recall"] == 1.0


def test_exact_match_boundary_mismatch():
    evaluator = NLPEvaluator(mode="exact")
    gt = [{"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}]
    pred = [{"start": 0, "end": 9, "type": "PERSON", "text": "John Smit"}]
    
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 0
    assert gm["fp"] == 1
    assert gm["fn"] == 1


def test_overlap_match_basic():
    evaluator = NLPEvaluator(mode="overlap", strict_type=True)
    gt = [{"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}]
    pred = [{"start": 5, "end": 15, "type": "PERSON", "text": "Smith Jones"}]
    
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 1
    assert gm["fp"] == 0
    assert gm["fn"] == 0
    assert gm["precision"] == 1.0
    assert gm["recall"] == 1.0
    assert gm["f1"] == 1.0


def test_overlap_match_no_overlap():
    evaluator = NLPEvaluator(mode="overlap")
    gt = [{"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}]
    pred = [{"start": 10, "end": 20, "type": "PERSON", "text": "Jane Miller"}]
    
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 0
    assert gm["fp"] == 1
    assert gm["fn"] == 1


def test_greedy_pairing_resolves_best_overlap():
    evaluator = NLPEvaluator(mode="overlap")
    gt = [{"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}]
    # pred1 overlaps slightly (5-15, iou = 5/15 = 0.33)
    # pred2 overlaps completely (0-10, iou = 10/10 = 1.0)
    pred = [
        {"start": 5, "end": 15, "type": "PERSON", "text": "Smith Jones"},
        {"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}
    ]
    
    # Under greedy matching, the 1.0 match is selected, and 5-15 is classified as FP
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 1
    assert gm["fp"] == 1
    assert gm["fn"] == 0


def test_one_to_one_constraint():
    evaluator = NLPEvaluator(mode="overlap")
    # Two ground truth entries overlap with a single large prediction
    gt = [
        {"start": 0, "end": 5, "type": "PERSON", "text": "John"},
        {"start": 6, "end": 10, "type": "PERSON", "text": "Smith"}
    ]
    pred = [
        {"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}
    ]
    
    # One prediction should match only one GT. The other GT should be unmatched (FN)
    report = evaluator.evaluate(gt, pred)
    gm = report["global_metrics"]
    
    assert gm["tp"] == 1
    assert gm["fp"] == 0
    assert gm["fn"] == 1
    assert gm["precision"] == 1.0
    assert gm["recall"] == 0.5


def test_empty_inputs():
    evaluator = NLPEvaluator()
    # Both empty
    report = evaluator.evaluate([], [])
    gm = report["global_metrics"]
    assert gm["tp"] == 0
    assert gm["fp"] == 0
    assert gm["fn"] == 0
    assert gm["precision"] == 1.0
    assert gm["recall"] == 1.0
    assert gm["f1"] == 1.0

    # Predictions empty
    gt = [{"start": 0, "end": 10, "type": "PERSON", "text": "John Smith"}]
    report = evaluator.evaluate(gt, [])
    gm = report["global_metrics"]
    assert gm["tp"] == 0
    assert gm["fp"] == 0
    assert gm["fn"] == 1
    assert gm["precision"] == 1.0
    assert gm["recall"] == 0.0
    assert gm["f1"] == 0.0


def test_multi_doc_micro_vs_macro():
    # Doc 1: GT=2, Pred=2, TP=2, FP=0, FN=0 (Precision=1.0, Recall=1.0)
    # Doc 2: GT=1, Pred=4, TP=1, FP=3, FN=0 (Precision=0.25, Recall=1.0)
    gt = {
        "doc1": [
            {"start": 0, "end": 5, "type": "PERSON", "text": "John"},
            {"start": 10, "end": 15, "type": "DATE", "text": "2026"}
        ],
        "doc2": [
            {"start": 0, "end": 5, "type": "PERSON", "text": "Jane"}
        ]
    }
    pred = {
        "doc1": [
            {"start": 0, "end": 5, "type": "PERSON", "text": "John"},
            {"start": 10, "end": 15, "type": "DATE", "text": "2026"}
        ],
        "doc2": [
            {"start": 0, "end": 5, "type": "PERSON", "text": "Jane"},
            {"start": 10, "end": 15, "type": "DATE", "text": "2026"},
            {"start": 20, "end": 25, "type": "LOCATION", "text": "Delhi"},
            {"start": 30, "end": 35, "type": "EMAIL", "text": "a@b.com"}
        ]
    }

    # Micro Aggregation:
    # Total GT = 3, Total Pred = 6
    # Total TP = 3, Total FP = 3, Total FN = 0
    # Global Precision = 3/6 = 0.5
    # Global Recall = 3/3 = 1.0
    # Global F1 = 2 * 0.5 * 1.0 / 1.5 = 2/3 = 0.6667
    evaluator_micro = NLPEvaluator(aggregation="micro")
    report_micro = evaluator_micro.evaluate(gt, pred)
    gm_micro = report_micro["global_metrics"]
    assert gm_micro["tp"] == 3
    assert gm_micro["fp"] == 3
    assert gm_micro["fn"] == 0
    assert abs(gm_micro["precision"] - 0.5) < 1e-6
    assert abs(gm_micro["recall"] - 1.0) < 1e-6

    # Macro Aggregation:
    # Doc 1 Precision = 1.0, Recall = 1.0, F1 = 1.0
    # Doc 2 Precision = 0.25, Recall = 1.0, F1 = 0.4
    # Macro Precision = (1.0 + 0.25) / 2 = 0.625
    # Macro Recall = (1.0 + 1.0) / 2 = 1.0
    # Macro F1 = (1.0 + 0.4) / 2 = 0.70
    evaluator_macro = NLPEvaluator(aggregation="macro")
    report_macro = evaluator_macro.evaluate(gt, pred)
    gm_macro = report_macro["global_metrics"]
    assert gm_macro["tp"] == 3
    assert gm_macro["fp"] == 3
    assert gm_macro["fn"] == 0
    assert abs(gm_macro["precision"] - 0.625) < 1e-6
    assert abs(gm_macro["recall"] - 1.0) < 1e-6
    assert abs(gm_macro["f1"] - 0.70) < 1e-6
