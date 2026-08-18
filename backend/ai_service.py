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
- Never invent IP addresses, subnet masks, gateways, interfaces, routes,
  command output, or other configuration values.
- If a required network value is unknown, refer to it generically.
- Evidence must come from the supplied case or rule checker findings.
- If evidence is insufficient, use lower confidence.
- Diagnose the fault before recommending a fix.
- Never claim that a fix has already been applied.
- Recommend safe Cisco troubleshooting steps.
- A human reviewer must approve, edit, or reject the diagnosis.
""".strip()


def diagnose_with_provider(case, rule_findings, provider):
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("GEMINI_BASE_URL")
        model = os.getenv("GEMINI_MODEL")
        temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))

        if not api_key or not base_url or not model:
            raise RuntimeError(
                "Gemini is not configured. Set GEMINI_API_KEY, "
                "GEMINI_BASE_URL, and GEMINI_MODEL."
            )

    elif provider == "lmstudio":
        api_key = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
        base_url = os.getenv(
            "LMSTUDIO_BASE_URL",
            "http://127.0.0.1:1234/v1"
        )
        model = os.getenv("LMSTUDIO_MODEL")

        if not model:
            raise RuntimeError(
                "LM Studio is not configured. Set LMSTUDIO_MODEL."
            )

        temperature = float(
            os.getenv("LMSTUDIO_TEMPERATURE", "0.2")
        )
        max_tokens = int(
            os.getenv("LMSTUDIO_MAX_TOKENS", "2000")
        )

    else:
        raise ValueError(
            "Unsupported AI provider. Use 'gemini' or 'lmstudio'."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are NetSage AI, a Cisco network troubleshooting "
                    "assistant operating as a decision-support system. "
                    "Return only valid JSON. "
                    "Ground every diagnosis in the supplied case and "
                    "deterministic rule-checker findings. "
                    "Never invent network configuration facts. "
                    "A human reviewer must approve, edit, or reject the result."
                )
            },
            {
                "role": "user",
                "content": build_prompt(case, rule_findings)
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "text"}
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            f"{provider.upper()} returned an empty response"
        )

    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{provider.upper()} returned invalid JSON"
        ) from error

    if not validate_response(result):
        raise ValueError(
            f"{provider.upper()} returned an invalid response structure"
        )

    return result


def diagnose(case, rule_findings, provider="lmstudio"):
    """
    Run diagnosis using exactly one selected AI provider.

    Supported providers:
        gemini
        lmstudio

    There is deliberately no deterministic AI fallback.
    Deterministic rule-checker findings are supplied to the AI
    as authoritative evidence.
    """

    if provider not in ("gemini", "lmstudio"):
        raise ValueError(
            "AI provider must be either 'gemini' or 'lmstudio'."
        )

    ai_response = diagnose_with_provider(
        case,
        rule_findings,
        provider
    )

    # A known deterministic finding remains authoritative.
    if rule_findings:
        ai_response["root_cause"] = rule_findings[0]

    return ai_response