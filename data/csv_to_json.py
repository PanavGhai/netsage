import csv
import json

csv_file = "data/cases.csv"
json_file = "data/cases.json"

with open(csv_file, "r", encoding="utf-8", newline="") as file:
    cases = list(csv.DictReader(file))

with open(json_file, "w", encoding="utf-8") as file:
    json.dump(cases, file, indent=2)

print(f"Converted {len(cases)} cases to {json_file}")