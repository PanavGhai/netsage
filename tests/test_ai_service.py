from backend import ai_service


def test_ai_response(monkeypatch):
    case = {
        "expected_fault": "PC has an incorrect gateway",
        "show_output": "Gateway: 192.168.20.1",
        "osi_layer": "Layer 3",
        "expected_next_command": "ipconfig /all",
        "expected_fix": "Set the correct gateway"
    }

    fake_response = {
        "root_cause": "PC has an incorrect gateway",
        "confidence": "High",
        "evidence": [
            "The supplied gateway does not match the expected configuration."
        ],
        "osi_layer": "Layer 3",
        "next_command": "ipconfig /all",
        "fix_steps": [
            "Set the correct gateway."
        ]
    }

    called = {}

    def fake_provider(case, rule_findings, provider):
        called["provider"] = provider
        return fake_response.copy()

    monkeypatch.setattr(
        ai_service,
        "diagnose_with_provider",
        fake_provider
    )

    response = ai_service.diagnose(case, [])

    assert called["provider"] == "lmstudio"
    assert ai_service.validate_response(response)
    assert response["root_cause"] == "PC has an incorrect gateway"


def test_checker_finding(monkeypatch):
    case = {
        "expected_fault": "Unknown",
        "show_output": "Gateway: 192.168.20.1",
        "osi_layer": "Layer 3",
        "expected_next_command": "ipconfig /all",
        "expected_fix": "Set the correct gateway"
    }

    findings = ["Gateway is outside the local subnet"]

    fake_response = {
        "root_cause": "Some AI-generated diagnosis",
        "confidence": "Medium",
        "evidence": [
            "Gateway is outside the local subnet."
        ],
        "osi_layer": "Layer 3",
        "next_command": "ipconfig /all",
        "fix_steps": [
            "Verify the configured default gateway."
        ]
    }

    called = {}

    def fake_provider(case, rule_findings, provider):
        called["provider"] = provider
        return fake_response.copy()

    monkeypatch.setattr(
        ai_service,
        "diagnose_with_provider",
        fake_provider
    )

    response = ai_service.diagnose(case, findings)

    assert called["provider"] == "lmstudio"
    assert response["root_cause"] == "Gateway is outside the local subnet"