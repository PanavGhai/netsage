import json
from pathlib import Path

from checker.rules import run_checks


root = Path(__file__).parent.parent
input_file = root / "checker" / "sample_input.json"

with open(input_file, encoding="utf-8") as file:
    data = json.load(file)

findings = run_checks(data)

print("Rule Checker Results:")

if findings:
    for finding in findings:
        print("-", finding)
else:
    print("No problems found")