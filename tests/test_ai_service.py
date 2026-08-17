from backend.ai_service import diagnose, validate_response


def test_ai_response():
    case = {
        "expected_fault": "PC has an incorrect gateway",
        "show_output": "Gateway: 192.168.20.1",
        "osi_layer": "Layer 3",
        "expected_next_command": "ipconfig /all",
        "expected_fix": "Set the correct gateway"
    }

    response = diagnose(case, [])

    assert validate_response(response)
    assert response["root_cause"] == "PC has an incorrect gateway"


def test_checker_finding():
    case = {
        "expected_fault": "Unknown",
        "show_output": "Gateway: 192.168.20.1",
        "osi_layer": "Layer 3",
        "expected_next_command": "ipconfig /all",
        "expected_fix": "Set the correct gateway"
    }

    findings = ["Gateway is outside the local subnet"]

    response = diagnose(case, findings)

    assert response["root_cause"] == "Gateway is outside the local subnet"