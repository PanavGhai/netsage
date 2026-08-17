import csv
from datetime import datetime


LOG_FILE = "logs/review_log.csv"


def review_diagnosis(case_id, ai_response, decision, final_root_cause=None, note=""):
    if decision not in ["Accepted", "Edited", "Rejected"]:
        raise ValueError("Invalid review decision")

    if decision == "Accepted":
        final_root_cause = ai_response["root_cause"]

    if decision == "Rejected":
        final_root_cause = ""

    row = {
        "case_id": case_id,
        "ai_root_cause": ai_response["root_cause"],
        "decision": decision,
        "final_root_cause": final_root_cause or "",
        "reviewer_note": note,
        "timestamp": datetime.now().isoformat()
    }

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(row)

    return row