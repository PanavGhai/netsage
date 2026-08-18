import csv
import json
from collections import Counter
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

from checker.rules import run_checks
from backend.ai_service import diagnose
from backend.review_service import review_diagnosis
from backend.verification import verify_review
from backend.evaluation import evaluate_diagnosis


app = Flask(__name__)
CORS(app)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = PROJECT_ROOT / "data" / "cases.json"
REVIEW_LOG_FILE = PROJECT_ROOT / "logs" / "review_log.csv"


def dashboard_metrics(cases_file=CASES_FILE, review_log_file=REVIEW_LOG_FILE):
    """Build presentation metrics from the case library and review audit log."""
    with open(cases_file, encoding="utf-8") as file:
        cases = json.load(file)

    concepts = Counter(case.get("concept", "Uncategorized") for case in cases)
    severities = Counter(case.get("severity", "Unspecified") for case in cases)
    decisions = Counter()

    reviews = []

    if Path(review_log_file).exists():
        with open(review_log_file, newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                reviews.append(row)

                decision = row.get("decision", "").strip()

                if decision:
                    decisions[decision] += 1

    reviewed = sum(decisions.values())
    agreements = decisions["Accepted"]

    # Keep only the latest review for each case.
    latest_reviews = {}

    for review in reviews:
        case_id = review.get("case_id", "").strip()

        if case_id:
            latest_reviews[case_id] = review

    # Compare the AI diagnosis with the case ground truth.
    ground_truth_matches = 0
    ground_truth_evaluated = 0

    case_lookup = {
        case.get("case_id"): case
        for case in cases
    }

    for review in latest_reviews.values():
        case_id = review.get("case_id", "").strip()
        ai_root_cause = review.get("ai_root_cause", "").strip()

        case = case_lookup.get(case_id)

        if not case or not ai_root_cause:
            continue

        evaluation = evaluate_diagnosis(
            case,
            {
                "root_cause": ai_root_cause
            }
        )

        ground_truth_evaluated += 1

        if evaluation["match"]:
            ground_truth_matches += 1

    ground_truth_accuracy = (
        round(
            (ground_truth_matches / ground_truth_evaluated) * 100,
            1
        )
        if ground_truth_evaluated
        else None
    )

    return {
        "case_count": len(cases),

        "issue_types": dict(sorted(concepts.items())),

        "severity_distribution": dict(sorted(severities.items())),

        "review_decisions": {
            decision: decisions[decision]
            for decision in ("Accepted", "Edited", "Rejected")
        },

        "agreement": {
            "accepted": agreements,
            "reviewed": reviewed,
            "rate": round(
                (agreements / reviewed) * 100,
                1
            ) if reviewed else None
        },

        "ground_truth": {
            "matches": ground_truth_matches,
            "evaluated": ground_truth_evaluated,
            "accuracy": ground_truth_accuracy
        }
    }


def process_case(
    case,
    config,
    review_decision,
    final_root_cause=None,
    note="",
    log_file="logs/review_log.csv",
    verification_log_file="logs/verification_log.csv"
):
    findings = run_checks(config)

    ai_response = diagnose(case, findings)

    review = review_diagnosis(
        case["case_id"],
        ai_response,
        review_decision,
        final_root_cause,
        note,
        log_file
    )

    verification = verify_review(
        review,
        verification_log_file
    )

    return {
        "case_id": case["case_id"],
        "checker_findings": findings,
        "ai_response": ai_response,
        "review": review,
        "verification": verification
    }


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "NetSage AI"
    })


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    return jsonify(dashboard_metrics())


@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    data = request.get_json()

    case = data.get("case")
    config = data.get("config", {})

    if not case:
        return jsonify({
            "error": "Case is required"
        }), 400

    findings = run_checks(config)
    ai_response = diagnose(case, findings)

    evaluation = evaluate_diagnosis(
        case,
        ai_response
    )

    return jsonify({
        "case_id": case["case_id"],
        "checker_findings": findings,
        "ai_response": ai_response,
        "evaluation": evaluation
    })

@app.route("/api/review", methods=["POST"])
def api_review():
    data = request.get_json()

    case = data.get("case")
    ai_response = data.get("ai_response")
    review_decision = data.get("review_decision")
    final_root_cause = data.get("final_root_cause")
    note = data.get("note", "")

    if not case:
        return jsonify({
            "error": "Case is required"
        }), 400

    if not ai_response:
        return jsonify({
            "error": "AI response is required"
        }), 400

    if review_decision not in ["Accepted", "Edited", "Rejected"]:
        return jsonify({
            "error": "Invalid review decision"
        }), 400

    review = review_diagnosis(
        case["case_id"],
        ai_response,
        review_decision,
        final_root_cause,
        note
    )

    verification = verify_review(review)

    return jsonify({
        "case_id": case["case_id"],
        "ai_response": ai_response,
        "review": review,
        "verification": verification
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
