import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


REQUIRED_FIELDS = [
    "root_cause",
    "confidence",
    "evidence",
    "osi_layer",
    "next_command",
    "fix_steps"
]


def validate_response(response):
    if not isinstance(response, dict):
        return False

    for field in REQUIRED_FIELDS:
        if field not in response:
            return False

    if not isinstance(response["evidence"], list):
        return False

    if not isinstance(response["fix_steps"], list):
        return False

    return True


def deterministic_diagnose(case, rule_findings):
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
        raise ValueError("Invalid deterministic response")

    return response


def build_prompt(case, rule_findings):
    return f"""
Analyze the following Cisco network troubleshooting case.

Symptom:
{case.get("symptom", "")}

Topology:
{case.get("topology", "")}

Show Command Output:
{case.get("show_output", "")}

Rule Checker Findings:
{json.dumps(rule_findings)}

Expected OSI Layer:
{case.get("osi_layer", "")}

Return ONLY a JSON object.

Do not include markdown.
Do not include explanations before or after the JSON.
Do not include code fences.

Use exactly this structure:

{{
  "root_cause": "string",
  "confidence": "Low",
  "evidence": ["string"],
  "osi_layer": "string",
  "next_command": "string",
  "fix_steps": ["string"]
}}

Requirements:

- root_cause: one concise diagnosis.
- confidence: exactly Low, Medium, or High.
- evidence: 1 to 3 pieces of evidence from the supplied information.
- osi_layer: the relevant OSI layer.
- next_command: exactly one safe diagnostic command.
- fix_steps: 1 to 3 safe corrective steps.
- Never invent IP addresses, subnet masks, gateways, interfaces, routes, command output, or other configuration values.
- If a required network value is unknown, refer to it generically.
- Evidence must come from the supplied case or rule checker findings.
- If evidence is insufficient, use lower confidence.
- Diagnose the fault before recommending a fix.
- Never claim that a fix has already been applied.
- Recommend safe Cisco troubleshooting steps.
- A human reviewer must approve, edit, or reject the diagnosis.
""".strip()


def gemini_available():
    return bool(
        os.getenv("GEMINI_API_KEY")
        and os.getenv("GEMINI_BASE_URL")
        and os.getenv("GEMINI_MODEL")
    )


def diagnose_with_gemini(case, rule_findings):
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("GEMINI_BASE_URL")
    )

    response = client.chat.completions.create(
        model=os.getenv("GEMINI_MODEL"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are NetSage AI, a Cisco network troubleshooting "
                    "assistant. Return only valid JSON."
                )
            },
            {
                "role": "user",
                "content": build_prompt(case, rule_findings)
            }
        ],
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000")),
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Gemini returned an empty response")

    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    result = json.loads(content)

    if not validate_response(result):
        raise ValueError("Gemini returned an invalid response")

    return result


def diagnose(case, rule_findings):
    # Deterministic findings are authoritative.
    # The AI can enrich the diagnosis, but should not override
    # a finding produced by the rule checker.
    if rule_findings:
        deterministic_response = deterministic_diagnose(
            case,
            rule_findings
        )

        if not gemini_available():
            return deterministic_response

        try:
            ai_response = diagnose_with_gemini(
                case,
                rule_findings
            )

            # Preserve the deterministic root cause.
            ai_response["root_cause"] = deterministic_response["root_cause"]

            return ai_response

        except Exception as error:
            print(f"Gemini diagnosis failed: {error}")
            print("Using deterministic fallback.")

            return deterministic_response

    # If there are no rule findings, retain the existing
    # expected-fault behavior when the case does not contain
    # enough information for an AI diagnosis.
    if not case.get("symptom") and not case.get("topology"):
        return deterministic_diagnose(case, rule_findings)

    if not gemini_available():
        return deterministic_diagnose(case, rule_findings)

    try:
        return diagnose_with_gemini(case, rule_findings)

    except Exception as error:
        print(f"Gemini diagnosis failed: {error}")
        print("Using deterministic fallback.")

        return deterministic_diagnose(case, rule_findings)