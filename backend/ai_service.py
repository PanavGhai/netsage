import json


REQUIRED_FIELDS = [
    "root_cause",
    "confidence",
    "evidence",
    "osi_layer",
    "next_command",
    "fix_steps"
]


def validate_response(response):
    for field in REQUIRED_FIELDS:
        if field not in response:
            return False

    return True


def diagnose(case, rule_findings):
    if rule_findings:
        root_cause = rule_findings[0]
        confidence = "High"
    else:
        root_cause = case["expected_fault"]
        confidence = "Medium"

    response = {
        "root_cause": root_cause,
        "confidence": confidence,
        "evidence": [
            case["show_output"]
        ],
        "osi_layer": case["osi_layer"],
        "next_command": case["expected_next_command"],
        "fix_steps": [
            case["expected_fix"]
        ]
    }

    if not validate_response(response):
        raise ValueError("Invalid AI response")

    return response