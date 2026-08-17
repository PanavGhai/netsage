from backend.verification import verify_review


def test_accepted_review():
    review = {
        "case_id": "NET-001",
        "decision": "Accepted"
    }

    result = verify_review(review)

    assert result["status"] == "Approved"


def test_edited_review():
    review = {
        "case_id": "NET-002",
        "decision": "Edited"
    }

    result = verify_review(review)

    assert result["status"] == "Approved"


def test_rejected_review():
    review = {
        "case_id": "NET-003",
        "decision": "Rejected"
    }

    result = verify_review(review)

    assert result["status"] == "Blocked"


def test_missing_review():
    review = {
        "case_id": "NET-004"
    }

    result = verify_review(review)

    assert result["status"] == "Blocked"