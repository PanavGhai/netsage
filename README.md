# NetSage AI

NetSage AI is an educational, human-in-the-loop network troubleshooting assistant for Cisco-style laboratory cases. It combines a deterministic rule checker with optional Gemini-powered analysis, then requires a human reviewer to accept, edit, or reject each diagnosis before verification is recorded.

It is a decision-support tool: it never applies network configuration changes or executes AI-generated commands.

## What it does

- Provides 30 structured troubleshooting cases covering topics including DHCP, DNS, routing, ACLs, NAT, VLANs, and wireless networking.
- Runs deterministic checks against supplied network configuration data, including gateway/subnet, VLAN, interface, and route checks.
- Uses Gemini through its OpenAI-compatible API when configured, with deterministic fallback if the service is unavailable or returns an invalid response.
- Returns a structured diagnosis: root cause, confidence, evidence, OSI layer, next diagnostic command, and recommended fix steps.
- Preserves deterministic checker findings as the root cause when a known rule finds a problem.
- Requires a human reviewer to accept, edit, or reject the recommendation.
- Marks accepted and edited reviews as `Approved`; rejected reviews are `Blocked`.
- Records review and verification decisions in CSV audit logs.

## Workflow

```text
Select case and provide configuration data
                |
                v
      Deterministic rule checks
                |
                v
 Gemini diagnosis or deterministic fallback
                |
                v
     Human review: accept / edit / reject
                |
                v
       Verification: approved / blocked
                |
                v
          Review and verification logs
```

The web dashboard makes the AI recommendation, human decision, and verification result separate states. An AI response alone is not an approved diagnosis.

## Architecture

| Component | Responsibility |
| --- | --- |
| `frontend/` | Browser dashboard for case selection, diagnosis, review, and verification status. |
| `backend/app.py` | Flask API and orchestration of diagnosis, review, and verification. |
| `checker/rules.py` | Deterministic checks for supplied configuration facts. |
| `backend/ai_service.py` | Gemini integration, response validation, and deterministic fallback. |
| `backend/review_service.py` | Records the human review decision. |
| `backend/verification.py` | Converts a review decision into an approved or blocked result. |
| `data/cases.json` | The case library used by the dashboard. |
| `logs/` | Runtime CSV audit logs for reviews and verification. |

## Requirements

- Python 3
- The packages in `requirements.txt`
- A Gemini API key only if you want live AI generation. Without one, NetSage uses its deterministic diagnosis fallback.

## Setup

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set `GEMINI_API_KEY` if you want Gemini enabled. Keep `.env` private; it is ignored by Git.

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=1000
```

The fallback path works when the Gemini variables are absent, unusable, or the provider returns an invalid response.

## Run the application

Start the Flask API in one PowerShell window:

```powershell
python -m backend.app
```

Then, in a second PowerShell window at the repository root, serve the frontend and case data:

```powershell
python -m http.server 8000
```

Open [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/) in a browser. The frontend sends API requests to `http://127.0.0.1:5000` when served outside Flask, and Flask enables CORS for this local setup.

Check that the API is available:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

Expected result:

```text
status  : ok
service : NetSage AI
```

## Demo walkthrough

1. Open the dashboard and choose a case from the case library.
2. Review the supplied symptom, topology, and command output.
3. Optionally enter IP address, subnet mask, and default gateway values to exercise the deterministic checks.
4. Select **Run AI diagnosis**.
5. Review the recommendation, supporting evidence, confidence, OSI layer, next command, and proposed fix steps.
6. Choose **Accept**, **Edit**, or **Reject**. Editing requires a corrected root cause.
7. Optionally add reviewer notes and select **Submit human review**.
8. Confirm the separate verification result: accepted/edited reviews are approved, while rejected diagnoses are blocked.

## API

### `GET /api/health`

Returns a small service-status response.

### `POST /api/diagnose`

Requires a `case` object and optional configuration data:

```json
{
  "case": { "case_id": "NET-001" },
  "config": {
    "ip": "192.168.10.10",
    "mask": "255.255.255.0",
    "gateway": "192.168.20.1"
  }
}
```

Returns `case_id`, `checker_findings`, and `ai_response`.

### `POST /api/review`

Requires the case, the returned AI response, and one of `Accepted`, `Edited`, or `Rejected`. It returns both the persisted review record and verification result.

## Testing

Run the automated suite from the repository root:

```powershell
python -m pytest
```

The suite currently contains 16 tests covering deterministic checks, response validation and fallback behavior, review decisions, verification rules, the full workflow, and rejection blocking.

## Safety and responsible AI

- The model is instructed to ground evidence in the supplied case and rule-checker findings.
- It is instructed not to invent addresses, interfaces, routes, command output, or other configuration facts.
- AI output must match a required JSON structure before use.
- Known deterministic findings remain authoritative for the root cause.
- The application does not automatically configure devices or execute suggested commands.
- Every diagnosis requires human review; rejection blocks verification.
- Gemini/API failure falls back to deterministic diagnosis rather than presenting a failed request as a successful AI result.

See [Responsible AI documentation](responsible_ai/responsible_ai_log.md) for the complete design rationale, limitations, privacy guidance, and responsible-use expectations.

## Limitations

NetSage is designed for educational Cisco-style troubleshooting cases and controlled lab environments. Rule coverage is limited to the implemented checks, and AI output can be incorrect even when valid JSON is returned. Review the evidence and recommendations before taking any network action; do not use the project as an autonomous production-network management system.

## Project layout

```text
backend/          Flask API, AI service, review, and verification
checker/          Deterministic network checks
data/             Case library and data utilities
frontend/         Dashboard HTML, CSS, and JavaScript
logs/             Runtime review and verification audit logs
responsible_ai/   Responsible-AI documentation
tests/            Automated pytest suite
```
