import csv
import json

from backend.app import dashboard_metrics


def test_dashboard_metrics_use_case_and_review_data(tmp_path):
    cases_file = tmp_path / "cases.json"
    review_file = tmp_path / "review.csv"

    cases_file.write_text(json.dumps([
        {"concept": "VLAN", "severity": "High"},
        {"concept": "DNS", "severity": "Medium"},
        {"concept": "VLAN", "severity": "High"}
    ]), encoding="utf-8")

    with review_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["decision"])
        writer.writeheader()
        writer.writerows([
            {"decision": "Accepted"},
            {"decision": "Edited"},
            {"decision": "Rejected"}
        ])

    metrics = dashboard_metrics(cases_file, review_file)

    assert metrics["case_count"] == 3
    assert metrics["issue_types"] == {"DNS": 1, "VLAN": 2}
    assert metrics["severity_distribution"] == {"High": 2, "Medium": 1}
    assert metrics["agreement"] == {"accepted": 1, "reviewed": 3, "rate": 33.3}
