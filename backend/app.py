from checker.rules import run_checks
from backend.ai_service import diagnose
from backend.review_service import review_diagnosis
from backend.verification import verify_review


def process_case(case, config, review_decision, final_root_cause=None, note=""):
    findings = run_checks(config)

    ai_response = diagnose(case, findings)

    review = review_diagnosis(
        case["case_id"],
        ai_response,
        review_decision,
        final_root_cause,
        note
    )

    verification = verify_review(review)

    return {
        "case_id": case["case_id"],
        "checker_findings": findings,
        "ai_response": ai_response,
        "review": review,
        "verification": verification
    }