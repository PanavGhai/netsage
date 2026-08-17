# NetSage AI — Setup Guide

## 1. Overview

NetSage AI is an AI-assisted Cisco network troubleshooting application with a human-in-the-loop review workflow.

The application consists of:

- A Flask backend
- A rule-based network checker
- An AI diagnosis service using the Gemini API through the OpenAI-compatible interface
- A browser-based frontend
- Human review and verification services
- Case data stored in JSON
- Audit logs for reviews and verification
- Automated tests using pytest

---

## 2. Requirements

Before setting up NetSage AI, install the following:

- Python 3.11 or newer
- Git
- A Google AI Studio API key
- A modern web browser

Python packages are listed in `requirements.txt`.

---

## 3. Clone the Repository

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd netsage
```

*(Replace `<repository-url>` with the URL of the NetSage AI repository.)*

---

## 4. Create a Python Virtual Environment

Creating a virtual environment keeps NetSage AI's dependencies isolated from other Python projects.

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 5. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The main dependencies include:
- `Flask`
- `Flask-CORS`
- `OpenAI` Python SDK
- `python-dotenv`
- `pytest`

---

## 6. Configure Environment Variables

NetSage AI uses environment variables for API configuration.
1. Create a local `.env` file in the project root.
2. The repository contains `.env.example` as a template.

Copy the example file:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

Open `.env` and configure the Gemini API settings. Example:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=1000
```

> **Security Note:** Do not commit the `.env` file to Git. The API key must remain private.

---

## 7. API Configuration

NetSage AI communicates with Gemini through an OpenAI-compatible API interface. The following variables control the AI service:

| Variable | Purpose |
| :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `GEMINI_BASE_URL` | OpenAI-compatible Gemini API endpoint |
| `GEMINI_MODEL` | Gemini model used for diagnosis |
| `GEMINI_TEMPERATURE` | Controls response variability |
| `GEMINI_MAX_TOKENS` | Maximum number of generated tokens |

> **Note:** The application does not require an API key to run its deterministic fallback logic. If the Gemini API is unavailable, the application falls back to the rule-based diagnosis system.

---

## 8. Verify the Project Structure

The project should contain the following major directories:

```text
netsage/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── ai_service.py
│   ├── review_service.py
│   └── verification.py
│
├── checker/
│   ├── __init__.py
│   ├── rules.py
│   ├── run_checker.py
│   ├── sample_input.json
│   └── sample_output.json
│
├── data/
│   ├── cases.csv
│   ├── cases.json
│   ├── csv_to_json.py
│   ├── raw/
│   └── processed/
│
├── dashboard/
│   ├── dashboard_data.json
│   └── dashboard_spec.md
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── assets/
│
├── logs/
│   ├── review_log.csv
│   └── verification_log.csv
│
├── prompts/
│   ├── diagnose_prompt.md
│   ├── system_prompt.md
│   └── few_shot_examples.md
│
├── responsible_ai/
│   └── responsible_ai_log.md
│
├── tests/
│   ├── test_ai_service.py
│   ├── test_app.py
│   ├── test_app_rejection.py
│   ├── test_checker.py
│   ├── test_review.py
│   └── test_verification.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 9. Run the Automated Tests

Run the complete test suite from the project root:

```bash
python -m pytest
```

A successful run should report all tests passing. Example:

```text
============================= test session starts =============================
collected 16 items

tests/test_ai_service.py .....
tests/test_app.py .
tests/test_app_rejection.py .
tests/test_checker.py ....
tests/test_review.py ....
tests/test_verification.py ....

============================= 16 passed =============================
```

*(The exact number of tests may change as the project is expanded.)*

---

## 10. Run the Backend

Start the Flask application:

```bash
python backend/app.py
```

The backend runs on: `http://127.0.0.1:5000`

The application exposes the following main endpoints:
- `GET  /api/health`
- `POST /api/diagnose`
- `POST /api/review`

---

## 11. Check Backend Health

With the backend running, open: `http://127.0.0.1:5000/api/health`

A successful response should look similar to:

```json
{
  "status": "ok",
  "service": "NetSage AI"
}
```

This confirms that the Flask backend is running.

---

## 12. Run the Frontend

The frontend is located in `frontend/`. It consists of:
- `index.html` — dashboard structure
- `styles.css` — dashboard styling
- `app.js` — frontend logic and backend communication

The frontend communicates with the Flask backend at `http://127.0.0.1:5000`.

The frontend loads troubleshooting cases from `/data/cases.json`.

When served by the Flask application, the frontend can be accessed through the application interface. If the frontend is being served separately during development, use a local HTTP server rather than opening `index.html` directly with `file://`.

For example:

```bash
python -m http.server 8000 --directory frontend
```

Then open: `http://127.0.0.1:8000`

*(The Flask backend must still be running on port 5000.)*

---

## 13. Using the Dashboard

The dashboard follows the complete NetSage AI workflow.

### Step 1 — Select a Case
Select a troubleshooting case from the case selector. The dashboard loads the case's:
- Case ID
- Symptoms
- Topology
- Show command output

### Step 2 — Enter Network Configuration
Enter the available network configuration:
- IP address
- Subnet mask
- Default gateway

These values are passed to the backend rule checker.

### Step 3 — Run Diagnosis
Select **Diagnose**. The backend performs rule-based checks first. The resulting findings are supplied to the AI diagnosis service.

The AI generates a structured diagnosis containing:
- Root cause
- Confidence
- Evidence
- OSI layer
- Next diagnostic command
- Recommended fix steps

### Step 4 — Review the AI Diagnosis
The generated diagnosis is displayed as an AI recommendation.
- The AI response is not automatically considered an approved network configuration.
- The recommended fix steps are informational only.
- NetSage AI does not automatically modify a Cisco device.

### Step 5 — Human Review
The reviewer must choose one of:
- **Accept**: The reviewer accepts the AI diagnosis without changing the root cause.
- **Edit**: The reviewer modifies the root cause before submitting the review.
- **Reject**: The reviewer rejects the diagnosis.

Reviewer notes can be provided for additional context.

### Step 6 — Submit Review
Select **Submit Review**. The frontend sends the review to `POST /api/review`. The backend records the review decision and performs verification.

### Step 7 — Verification
The verification service evaluates the human review. Possible states include:
- **Pending**
- **Approved**
- **Blocked**

Accepted and edited diagnoses may proceed to verification. Rejected diagnoses are blocked.

---

## 14. Rule Checker

The rule checker provides deterministic network troubleshooting findings. The checker is located in `checker/rules.py`.

Its purpose is to identify known configuration problems before the AI is asked to provide additional reasoning. This provides a deterministic foundation for the AI-assisted workflow.

When rule findings are available, the AI may enrich the diagnosis but does not replace the authoritative checker finding as the root cause.

---

## 15. AI Diagnosis

The AI service is located in `backend/ai_service.py`.

The AI receives information such as:
- Symptoms
- Network topology
- Show command output
- Rule checker findings
- Relevant OSI layer

The expected response is a JSON object containing:

```json
{
  "root_cause": "string",
  "confidence": "Low",
  "evidence": [
    "string"
  ],
  "osi_layer": "string",
  "next_command": "string",
  "fix_steps": [
    "string"
  ]
}
```

The service validates the returned structure before accepting the diagnosis.

---

## 16. Deterministic Fallback

NetSage AI is designed to continue operating when the Gemini API is unavailable.

If the AI service:
- Has no configured API key
- Encounters an API error
- Receives invalid JSON
- Receives an invalid response structure
- Encounters another diagnosis failure

...the application uses deterministic fallback logic.

This prevents an external AI failure from completely stopping the troubleshooting workflow.

---

## 17. Human-in-the-Loop Safety

AI output is treated as a recommendation. The workflow requires human review before verification:

$$\text{AI Recommendation} \longrightarrow \text{Human Review} \longrightarrow \text{Accepted / Edited / Rejected} \longrightarrow \text{Verification}$$

- The AI does not directly apply network configuration changes.
- All recommended fixes must be reviewed by a human before being treated as an approved diagnosis.

---

## 18. Logging

NetSage AI records review and verification information in the `logs/` directory.

- **Review Log** (`logs/review_log.csv`): Records human review decisions and related information.
- **Verification Log** (`logs/verification_log.csv`): Records verification results.

These logs provide an audit trail for the human-in-the-loop workflow.

---

## 19. Responsible AI Documentation

Responsible AI design information is documented in `responsible_ai/responsible_ai_log.md`.

This documentation covers areas such as:
- Human oversight
- AI limitations
- Deterministic rule checking
- AI fallback behavior
- Evidence requirements
- Prevention of invented network values
- Review and verification
- Auditability

The responsible AI documentation is separate from the technical setup instructions in this file.

---

## 20. Troubleshooting

### Backend Will Not Start
Check that the virtual environment is active:
```powershell
.venv\Scripts\Activate.ps1
```
Then reinstall dependencies and start again:
```bash
pip install -r requirements.txt
python backend/app.py
```

### Gemini API Does Not Respond
Check that `.env` contains valid values:
```env
GEMINI_API_KEY=your_api_key
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-3.6-flash
```
Also check the API quota associated with the Google AI Studio project. If Gemini is unavailable, NetSage AI should use its deterministic fallback.

### Frontend Cannot Connect to Backend
Make sure the Flask backend is running (`python backend/app.py`) and confirm that `http://127.0.0.1:5000/api/health` returns a successful health response. If the frontend is being served separately, confirm that the frontend is using the same backend address.

### Cases Do Not Load
Verify that `data/cases.json` exists and contains valid JSON. If the case data was modified from the CSV source, regenerate the JSON using:
```bash
python data/csv_to_json.py
```

### Tests Fail
Run `python -m pytest`, read the failing test name and traceback. Do not ignore failing tests before committing changes. After making a fix, run the complete test suite again.

---

## 21. Development Workflow

A recommended development workflow is:

1. Activate virtual environment
2. Install/update dependencies
3. Configure `.env`
4. Run automated tests
5. Start Flask backend
6. Open the frontend
7. Test the troubleshooting workflow
8. Review generated diagnosis
9. Test Accept, Edit, and Reject
10. Verify logs
11. Run pytest again
12. Commit changes

---

## 22. Git Safety

The following files should **not** be committed:
- `.env`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`

The `.env.example` file may be committed because it contains configuration placeholders rather than the actual API key.

> **Warning:** Never commit a real API key to the repository. If an API key is accidentally committed, revoke it immediately and replace it with a new key.

---

## 23. Quick Start

For an already configured development environment:

**Terminal 1 — Backend:**
```powershell
.venv\Scripts\Activate.ps1
python backend/app.py
```

**Terminal 2 — Frontend:**
```bash
python -m http.server 8000 --directory frontend
```

- Open frontend: `http://127.0.0.1:8000`
- Backend remains available at: `http://127.0.0.1:5000`

---

## 24. Validation Checklist

Before considering the local setup complete, verify:

- [ ] Python environment is active
- [ ] Dependencies are installed
- [ ] `.env` is configured
- [ ] API key is not committed
- [ ] Automated tests pass
- [ ] Flask backend starts successfully
- [ ] `/api/health` responds successfully
- [ ] Frontend loads successfully
- [ ] Cases can be selected
- [ ] Network configuration can be entered
- [ ] Diagnosis can be requested
- [ ] AI diagnosis is displayed
- [ ] Human review can be selected
- [ ] Reviewer notes can be submitted
- [ ] Accepted diagnosis can be verified
- [ ] Edited diagnosis can be verified
- [ ] Rejected diagnosis is blocked
- [ ] Review logs are updated
- [ ] Verification logs are updated

---

## 25. Project Status

NetSage AI is intended as an AI-assisted troubleshooting prototype.

It demonstrates:
- Rule-based network checking
- AI-assisted diagnosis
- Structured AI responses
- Human-in-the-loop review
- Verification
- Audit logging
- Responsible AI controls
- Automated testing
- Browser-based interaction

It is **not** intended to automatically modify production network infrastructure. Any real network change should be performed manually by an appropriately authorized network administrator after reviewing the diagnosis and recommended remediation.