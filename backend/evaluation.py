def evaluate_diagnosis(case, ai_response):
    expected = str(case.get("expected_fault", "")).strip().lower()
    actual = str(ai_response.get("root_cause", "")).strip().lower()

    if not expected or not actual:
        return {
            "match": False,
            "expected_fault": case.get("expected_fault", ""),
            "ai_root_cause": ai_response.get("root_cause", "")
        }

    match = expected in actual or actual in expected

    return {
        "match": match,
        "expected_fault": case.get("expected_fault", ""),
        "ai_root_cause": ai_response.get("root_cause", "")
    }