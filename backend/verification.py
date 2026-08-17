import csv
from datetime import datetime


LOG_FILE = "logs/verification_log.csv"


def verify_review(review, log_file=LOG_FILE):
    decision = review.get("decision")

    if decision == "Rejected":
        status = "Blocked"
        reason = "Human reviewer rejected the diagnosis"
    elif decision in ["Accepted", "Edited"]:
        status = "Approved"
        reason = "Human reviewer approved the diagnosis"
    else:
        status = "Blocked"
        reason = "No valid human review decision"

    result = {
        "case_id": review.get("case_id", ""),
        "decision": decision or "",
        "status": status,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }

    with open(log_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=result.keys())

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(result)

    return result