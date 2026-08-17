from checker.rules import run_checks
from backend.ai_service import diagnose
from backend.review_service import review_diagnosis
from backend.verification import verify_review


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