# NetSage AI — System Architecture

## 1. Overview

NetSage AI is an AI-assisted network troubleshooting system designed for Cisco Packet Tracer and Cisco-style laboratory networks.

The system combines deterministic network rule checking with an AI diagnosis service. The deterministic checker identifies known configuration problems, while the AI service interprets the supplied network evidence and produces a structured troubleshooting recommendation.

NetSage AI follows a Human-in-the-Loop design. An AI-generated diagnosis is treated as a recommendation and must pass through human review before verification.

The system does not automatically modify network configurations.

---

## 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      Frontend        │
                         │  HTML / CSS / JS     │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │     Flask Backend    │
                         │      /api/*          │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
            ┌─────────────────┐          ┌─────────────────┐
            │   Rule Checker  │          │   AI Service    │
            │  Deterministic  │          │     Gemini      │
            │    Analysis     │          │   + Fallback    │
            └────────┬────────┘          └────────┬────────┘
                     │                            │
                     └──────────────┬─────────────┘
                                    ▼
                           ┌──────────────────┐
                           │  AI Diagnosis    │
                           │ Structured JSON  │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │  Human Review    │
                           │ Accept / Edit /  │
                           │ Reject           │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │   Verification   │
                           │ Approved/Blocked │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │    Audit Logs    │
                           │ Review / Verify  │
                           └──────────────────┘
```

---

## 3. Repository Architecture

```text
netsage/
│
├── backend/
│   ├── app.py
│   ├── ai_service.py
│   ├── review_service.py
│   ├── verification.py
│   └── __init__.py
│
├── checker/
│   ├── rules.py
│   ├── run_checker.py
│   ├── sample_input.json
│   ├── sample_output.json
│   └── __init__.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── assets/
│
├── data/
│   ├── cases.csv
│   ├── cases.json
│   └── csv_to_json.py
│
├── prompts/
│   ├── system_prompt.md
│   ├── diagnose_prompt.md
│   └── few_shot_examples.md
│
├── dashboard/
│   ├── dashboard_spec.md
│   └── dashboard_data.json
│
├── logs/
│   ├── review_log.csv
│   └── verification_log.csv
│
├── responsible_ai/
│   └── responsible_ai_log.md
│
├── docs/
│   ├── architecture.md
│   ├── case_schema.md
│   ├── demo.md
│   └── setup.md
│
└── tests/
    ├── test_ai_service.py
    ├── test_app.py
    ├── test_app_rejection.py
    ├── test_checker.py
    ├── test_review.py
    └── test_verification.py
```

---

## 4. Frontend Layer

The frontend provides the user-facing troubleshooting dashboard.

### Technologies

- HTML
- CSS
- JavaScript

### Responsibilities

The frontend allows the user to:

1. Select a troubleshooting case.
2. View the case symptoms.
3. View topology information.
4. View supplied command output.
5. Enter network configuration information.
6. Request an AI diagnosis.
7. Review the AI-generated diagnosis.
8. Accept, edit, or reject the diagnosis.
9. Add reviewer notes.
10. Submit the human review.
11. View the verification result.

The frontend does not directly communicate with Gemini. AI communication occurs through the Flask backend.

---

## 5. Backend Layer

The backend is implemented using Flask.

The primary application is:

```text
backend/app.py
```

The backend exposes the following endpoints.

### Health Endpoint

```text
GET /api/health
```

Used to confirm that the NetSage backend is running.

Example response:

```json
{
  "status": "ok",
  "service": "NetSage AI"
}
```

### Diagnosis Endpoint

```text
POST /api/diagnose
```

Receives:

- troubleshooting case
- network configuration

The backend then:

1. Runs the deterministic rule checker.
2. Sends the case and rule findings to the AI service.
3. Receives a structured diagnosis.
4. Returns the checker findings and AI response.

### Review Endpoint

```text
POST /api/review
```

Receives:

- case
- AI response
- review decision
- final root cause
- reviewer note

The backend then:

1. Processes the human review.
2. Records the review.
3. Passes the review to the verification system.
4. Returns the review and verification result.

---

## 6. Rule Checker

The deterministic rule checker is implemented in:

```text
checker/rules.py
```

Its purpose is to identify network problems that can be determined using explicit rules.

Examples include:

- Incorrect default gateway
- Missing route
- VLAN-related configuration problems
- Other deterministic network configuration errors supported by the rule set

The checker does not rely on an AI model.

This provides a deterministic source of evidence that can be used by the AI service.

### Rule Checker Authority

When the rule checker produces a deterministic finding, the finding is treated as authoritative for the root cause.

The AI may provide additional evidence, explanation, or recommendations, but it must not override the deterministic finding.

This reduces the risk of an AI response contradicting an explicitly detected configuration error.

---

## 7. AI Service

The AI service is implemented in:

```text
backend/ai_service.py
```

The service uses an OpenAI-compatible client interface to communicate with the Gemini API.

The model configuration is supplied through environment variables.

The AI receives:

- Network symptom
- Topology
- Show command output
- Rule checker findings
- Expected OSI layer

The AI is instructed to return a structured JSON diagnosis.

The expected response contains:

```json
{
  "root_cause": "string",
  "confidence": "Low, Medium, or High",
  "evidence": [],
  "osi_layer": "string",
  "next_command": "string",
  "fix_steps": []
}
```

---

## 8. AI Response Validation

Before an AI response is accepted by the application, it is checked for the required fields.

Required fields are:

- `root_cause`
- `confidence`
- `evidence`
- `osi_layer`
- `next_command`
- `fix_steps`

The application also verifies that:

- the response is a JSON object
- `evidence` is a list
- `fix_steps` is a list

Invalid AI responses are rejected.

---

## 9. Deterministic Fallback

NetSage AI does not depend entirely on the availability of the external AI service.

If Gemini:

- exceeds its API quota
- returns invalid JSON
- returns an empty response
- encounters another API error
- is not configured

the application uses the deterministic diagnosis path.

The fallback uses the rule checker findings when available.

If no rule findings are available, it can use the case's expected fault information as the deterministic fallback.

This allows the application to continue operating when the external AI service is unavailable.

---

## 10. Prompt Architecture

Prompt material is stored separately from the backend implementation.

```text
prompts/
├── system_prompt.md
├── diagnose_prompt.md
└── few_shot_examples.md
```

### System Prompt

Defines the role and safety constraints of NetSage AI.

### Diagnosis Prompt

Defines the information supplied to the model and the required response format.

### Few-Shot Examples

Provide representative troubleshooting examples to guide the expected diagnosis format and reasoning style.

The application also constructs the active diagnosis prompt programmatically in `backend/ai_service.py`.

---

## 11. Human Review Layer

The human review system is implemented in:

```text
backend/review_service.py
```

Every AI diagnosis must undergo human review.

The reviewer can select:

```text
Accepted
Edited
Rejected
```

### Accepted

The reviewer accepts the AI diagnosis without changing the root cause.

### Edited

The reviewer modifies the diagnosis before submitting it.

### Rejected

The reviewer rejects the AI recommendation.

A rejected diagnosis cannot proceed as an approved result.

---

## 12. Verification Layer

The verification system is implemented in:

```text
backend/verification.py
```

Its purpose is to determine whether the reviewed diagnosis is allowed to proceed.

The primary verification states are:

```text
Pending
Approved
Blocked
```

The workflow is:

```text
AI Diagnosis
     │
     ▼
Human Review
     │
 ┌───┼────────┐
 ▼   ▼        ▼
Accept Edit  Reject
 │     │       │
 ▼     ▼       ▼
Approved      Blocked
```

Accepted and edited diagnoses can proceed to verification.

Rejected diagnoses are blocked.

---

## 13. Audit Logging

NetSage records human review and verification results.

### Review Log

```text
logs/review_log.csv
```

Records human review decisions and associated information.

### Verification Log

```text
logs/verification_log.csv
```

Records verification outcomes.

These logs provide an audit trail showing how an AI recommendation was handled after generation.

AI recommendations are therefore not treated as final decisions simply because they were generated.

---

## 14. Data Layer

The primary troubleshooting cases are stored in:

```text
data/cases.json
```

A CSV representation is also maintained:

```text
data/cases.csv
```

The conversion utility is:

```text
data/csv_to_json.py
```

The frontend loads the JSON case dataset.

The cases contain structured information such as:

- Case ID
- Concept
- Symptom
- Topology
- Show command output
- Expected fault
- OSI layer
- Expected next diagnostic command
- Expected fix

The expected-fault fields are used for deterministic fallback and testing; they are not presented as evidence generated by the AI.

---

## 15. Human-in-the-Loop Architecture

Human oversight is a core architectural requirement.

The system separates:

```text
AI Recommendation
```

from:

```text
Human-Approved Result
```

The AI can recommend a diagnosis and corrective steps, but it cannot independently approve or apply a network configuration change.

The review layer provides the decision boundary between AI output and verification.

This architecture is intended to reduce the risk of:

- unsupported AI recommendations
- hallucinated network values
- automatic configuration changes
- unreviewed AI decisions

---

## 16. Safety Boundaries

NetSage AI is designed as a troubleshooting assistant rather than an autonomous network configuration system.

The AI is instructed to:

- use only supplied evidence
- avoid inventing network values
- avoid inventing command output
- lower confidence when evidence is insufficient
- recommend diagnosis before corrective action
- recommend safe diagnostic commands
- never claim that a configuration change has already been performed

The application does not automatically execute the recommended Cisco commands.

Fix steps shown by the system are recommendations for a human operator to review.

---

## 17. Error and Failure Handling

The application has multiple layers of failure handling.

### Missing Case

The API rejects a diagnosis request if no case is supplied.

### AI API Failure

If Gemini is unavailable or fails, the deterministic fallback is used.

### Invalid AI Response

If the AI returns malformed or incomplete JSON, the response is rejected and the deterministic fallback is used.

### Invalid Review Decision

The review endpoint accepts only:

```text
Accepted
Edited
Rejected
```

### Backend Connection Failure

The frontend displays an error when it cannot communicate with the backend.

---

## 18. Testing Architecture

Automated tests are stored in:

```text
tests/
```

The current test suite covers:

- AI service behavior
- API behavior
- rejected review behavior
- rule checker behavior
- human review behavior
- verification behavior

The test suite can be executed with:

```powershell
python -m pytest
```

All core components are tested independently as well as through API-level behavior.

---

## 19. End-to-End Workflow

The complete NetSage workflow is:

```text
1. User selects a case
        ↓
2. Frontend displays network evidence
        ↓
3. User provides/inspects configuration
        ↓
4. POST /api/diagnose
        ↓
5. Rule Checker analyzes configuration
        ↓
6. AI Service receives case + evidence
        ↓
7. Gemini generates structured diagnosis
        ↓
8. AI response is validated
        ↓
9. Deterministic finding remains authoritative
        ↓
10. Diagnosis is displayed
        ↓
11. Human reviewer evaluates recommendation
        ↓
12. Accept / Edit / Reject
        ↓
13. Review is recorded
        ↓
14. Verification evaluates the review
        ↓
15. Approved or Blocked result is returned
        ↓
16. Review and verification records are preserved
```

---

## 20. Architectural Design Principles

NetSage AI follows these primary principles:

### Deterministic Before Generative

Known configuration problems are identified using deterministic rules before relying on generative AI.

### Evidence-Based Diagnosis

The AI is instructed to use only supplied case information and rule checker findings.

### Structured Output

AI responses use a predefined JSON schema rather than unrestricted natural-language output.

### Human Oversight

AI recommendations require human review before being considered approved.

### Fail-Safe Behavior

AI service failures do not cause the entire troubleshooting workflow to fail when deterministic information is available.

### No Autonomous Configuration Changes

The system provides recommendations but does not directly modify network devices.

### Auditability

Human review and verification outcomes are recorded in persistent logs.

---

## 21. Current System Scope

The current implementation is intended for controlled Cisco Packet Tracer and Cisco-style laboratory troubleshooting scenarios.

It is not an autonomous network management system.

The system does not:

- connect directly to physical Cisco devices
- automatically execute configuration commands
- automatically repair network configurations
- guarantee that an AI recommendation is correct
- replace human network engineering judgment

The AI component is an assistance layer within a larger deterministic and human-reviewed troubleshooting workflow.