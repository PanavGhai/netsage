from backend.app import process_case


def test_rejected_diagnosis_is_blocked():
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

    result = process_case(
        case,
        config,
        "Rejected",
        note="AI diagnosis rejected by reviewer"
    )

    assert result["review"]["decision"] == "Rejected"
    assert result["verification"]["status"] == "Blocked"