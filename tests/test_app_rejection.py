from backend.app import app


def test_rejected_diagnosis_is_blocked(tmp_path, monkeypatch):
    case = {
        "case_id": "NET-002",
        "expected_fault": "Incorrect gateway",
        "show_output": "Gateway: 192.168.20.1",
        "osi_layer": "Layer 3",
        "expected_next_command": "ipconfig /all",
        "expected_fix": "Set the correct gateway"
    }

    config = {
        "ip": "192.168.10.10",
        "mask": "255.255.255.0",
        "gateway": "192.168.20.1"
    }

    ai_response = {
        "root_cause": "Incorrect gateway",
        "confidence": 0.95,
        "osi_layer": "Layer 3",
        "evidence": [
            "Gateway is outside the local subnet"
        ],
        "next_command": "ipconfig /all",
        "fix_steps": [
            "Set the correct gateway"
        ]
    }

    monkeypatch.setattr(
        "backend.app.diagnose",
        lambda case, findings, provider: ai_response
    )

    monkeypatch.setattr(
        "backend.app.REVIEW_LOG_FILE",
        tmp_path / "review.csv"
    )

    monkeypatch.setattr(
        "backend.app.VERIFICATION_LOG_FILE",
        tmp_path / "verification.csv"
    )

    client = app.test_client()

    diagnosis_response = client.post(
        "/api/diagnose",
        json={
            "case": case,
            "config": config,
            "provider": "lmstudio"
        }
    )

    assert diagnosis_response.status_code == 200

    diagnosis = diagnosis_response.get_json()

    review_response = client.post(
        "/api/review",
        json={
            "case": case,
            "config": config,
            "ai_response": diagnosis["ai_response"],
            "review_decision": "Rejected",
            "final_root_cause": "",
            "note": "AI diagnosis rejected by reviewer"
        }
    )

    assert review_response.status_code == 200

    result = review_response.get_json()

    assert result["review"]["decision"] == "Rejected"
    assert result["verification"]["status"] == "Blocked"