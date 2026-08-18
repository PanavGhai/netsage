from backend.evaluation import evaluate_diagnosis


def test_wrong_vlan_assignment_matches():
    case = {
        "expected_fault": "PC2 is assigned to the wrong VLAN"
    }

    ai_response = {
        "root_cause": "Interface is assigned to the wrong VLAN"
    }

    result = evaluate_diagnosis(case, ai_response)

    assert result["match"] is True


def test_exact_fault_matches():
    case = {
        "expected_fault": "PC2 is assigned to the wrong VLAN"
    }

    ai_response = {
        "root_cause": "PC2 is assigned to the wrong VLAN"
    }

    result = evaluate_diagnosis(case, ai_response)

    assert result["match"] is True


def test_different_fault_does_not_match():
    case = {
        "expected_fault": "PC2 is assigned to the wrong VLAN"
    }

    ai_response = {
        "root_cause": "The default gateway is incorrect"
    }

    result = evaluate_diagnosis(case, ai_response)

    assert result["match"] is False