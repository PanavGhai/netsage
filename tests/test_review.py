from backend.review_service import review_diagnosis


def test_accepted_review(tmp_path):
    response = {
        "root_cause": "Incorrect gateway"
    }

    result = review_diagnosis(
        "NET-001",
        response,
        "Accepted",
        log_file=tmp_path / "review.csv"
    )

    assert result["decision"] == "Accepted"
    assert result["final_root_cause"] == "Incorrect gateway"


def test_edited_review(tmp_path):
    response = {
        "root_cause": "DNS failure"
    }

    result = review_diagnosis(
        "NET-002",
        response,
        "Edited",
        "Incorrect gateway",
        "Evidence showed gateway problem",
        tmp_path / "review.csv"
    )

    assert result["decision"] == "Edited"
    assert result["final_root_cause"] == "Incorrect gateway"


def test_rejected_review(tmp_path):
    response = {
        "root_cause": "DNS failure"
    }

    result = review_diagnosis(
        "NET-003",
        response,
        "Rejected",
        note="Diagnosis was not supported",
        log_file=tmp_path / "review.csv"
    )

    assert result["decision"] == "Rejected"
    assert result["final_root_cause"] == ""


def test_invalid_review(tmp_path):
    response = {
        "root_cause": "DNS failure"
    }

    try:
        review_diagnosis(
            "NET-004",
            response,
            "Invalid",
            log_file=tmp_path / "review.csv"
        )
        assert False
    except ValueError:
        assert True