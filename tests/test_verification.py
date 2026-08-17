from backend.verification import verify_review


def test_accepted_review(tmp_path):
    review = {
        "case_id": "NET-001",
        "decision": "Accepted"
    }

    result = verify_review(
        review,
        tmp_path / "verification.csv"
    )

    assert result["status"] == "Approved"


def test_edited_review(tmp_path):
    review = {
        "case_id": "NET-002",
        "decision": "Edited"
    }

    result = verify_review(
        review,
        tmp_path / "verification.csv"
    )

    assert result["status"] == "Approved"


def test_rejected_review(tmp_path):
    review = {
        "case_id": "NET-003",
        "decision": "Rejected"
    }

    result = verify_review(
        review,
        tmp_path / "verification.csv"
    )

    assert result["status"] == "Blocked"


def test_missing_review(tmp_path):
    review = {
        "case_id": "NET-004"
    }

    result = verify_review(
        review,
        tmp_path / "verification.csv"
    )

    assert result["status"] == "Blocked"