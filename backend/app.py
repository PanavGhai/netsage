from flask import Flask, request, jsonify
from flask_cors import CORS

from checker.rules import run_checks
from backend.ai_service import diagnose
from backend.review_service import review_diagnosis
from backend.verification import verify_review


app = Flask(__name__)
CORS(app)


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

    return jsonify({
        "case_id": case["case_id"],
        "checker_findings": findings,
        "ai_response": ai_response
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