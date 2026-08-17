from backend.review_service import review_diagnosis


def test_accepted_review():
    response = {
        "root_cause": "Incorrect gateway"
    }

    result = review_diagnosis(
        "NET-001",
        response,
        "Accepted"
    )

    assert result["decision"] == "Accepted"
    assert result["final_root_cause"] == "Incorrect gateway"


def test_edited_review():
    response = {
        "root_cause": "DNS failure"
    }

    result = review_diagnosis(
        "NET-002",
        response,
        "Edited",
        "Incorrect gateway",
        "Evidence showed gateway problem"
    )

    assert result["decision"] == "Edited"
    assert result["final_root_cause"] == "Incorrect gateway"


def test_rejected_review():
    response = {
        "root_cause": "DNS failure"
    }

    result = review_diagnosis(
        "NET-003",
        response,
        "Rejected",
        note="Diagnosis was not supported by evidence"
    )

    assert result["decision"] == "Rejected"
    assert result["final_root_cause"] == ""


def test_invalid_review():
    response = {
        "root_cause": "DNS failure"
    }

    try:
        review_diagnosis(
            "NET-004",
            response,
            "Invalid"
        )
        assert False
    except ValueError:
        assert True