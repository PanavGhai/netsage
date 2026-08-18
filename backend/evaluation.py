def normalize(text):
    return " ".join(
        str(text).strip().lower().split()
    )


FAULT_ALIASES = {
    "wrong vlan assignment": [
        "pc2 is assigned to the wrong vlan",
        "interface is assigned to the wrong vlan",
        "interface is in the wrong vlan",
        "incorrect vlan assignment",
        "wrong vlan assignment",
    ]
}


def faults_match(expected, actual):
    expected = normalize(expected)
    actual = normalize(actual)

    if not expected or not actual:
        return False

    # Exact match.
    if expected == actual:
        return True

    # Existing substring matching.
    if expected in actual or actual in expected:
        return True

    # Match known equivalent fault descriptions.
    for aliases in FAULT_ALIASES.values():
        normalized_aliases = [
            normalize(alias)
            for alias in aliases
        ]

        if expected in normalized_aliases and actual in normalized_aliases:
            return True

    return False


def evaluate_diagnosis(case, ai_response):
    expected = case.get("expected_fault", "")
    actual = ai_response.get("root_cause", "")

    match = faults_match(expected, actual)

    return {
        "match": match,
        "expected_fault": expected,
        "ai_root_cause": actual
    }