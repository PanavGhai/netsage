# NetSage AI Demo Guide

## Purpose

This document describes how to demonstrate the NetSage AI troubleshooting workflow from case selection through human review and verification.

The demonstration shows the complete Human-in-the-Loop workflow:

1. Select a network troubleshooting case.
2. Provide or review network evidence.
3. Run the rule-based checker.
4. Generate an AI-assisted diagnosis.
5. Review the diagnosis.
6. Accept, edit, or reject the diagnosis.
7. Submit the human review.
8. Display the verification result.
9. Demonstrate that the workflow is recorded in the project logs.

---

## Prerequisites

Before running the demonstration, ensure that:

- Python is installed.
- Project dependencies are installed.
- The repository has been cloned or downloaded.
- The `.env` file contains the required Gemini configuration.
- The backend dependencies are available.
- The test suite passes.

Run the test suite with:

```powershell
python -m pytest
```

Expected result:
- `16 passed` (The exact number of tests may increase as the project is expanded).

---

## Starting NetSage

From the project root, run:

```bash
python backend/app.py
```

- The Flask backend runs on: `http://127.0.0.1:5000`
- The backend health endpoint can be tested at: `http://127.0.0.1:5000/api/health`

A successful response should contain:

```json
{
  "status": "ok",
  "service": "NetSage AI"
}
```

---

## Opening the Frontend

The frontend is located in `frontend/`. Open `frontend/index.html` using a local development server or the configured project serving method.

The dashboard provides the following workflow sections:
- **Case**
- **AI Diagnosis**
- **Human Review**
- **Verification**

---

## Demonstration Workflow

### Step 1 — Select a Case

Use the **Case** selector to choose one of the troubleshooting cases.

The selected case should populate information such as:
- Case ID
- Symptoms
- Topology
- Show command output

The case data is loaded from `data/cases.json`.

### Step 2 — Enter Network Configuration

Enter the available network configuration values where applicable:
- IP address
- Subnet mask
- Default gateway

These values are provided to the backend rule checker. The checker evaluates the supplied configuration for known networking problems before the AI diagnosis is generated.

### Step 3 — Run Diagnosis

Select **Diagnose**. The frontend sends the case and network configuration to `POST /api/diagnose`.

The backend then:
1. Receives the case.
2. Runs the deterministic network checker.
3. Collects rule-based findings.
4. Passes the case and findings to the AI service.
5. Validates the AI response.
6. Uses the deterministic result as a fallback if the AI service is unavailable or returns an invalid response.
7. Returns the diagnosis to the frontend.

### Step 4 — Review the AI Diagnosis

The **AI Diagnosis** section displays:
- Root cause
- Confidence
- OSI layer
- Evidence
- Next diagnostic command
- Recommended fix steps

The diagnosis is presented as an AI recommendation. It is not automatically considered an approved network change. The recommended fix steps are informational and do not directly modify a Cisco device.

### Step 5 — Human Review

The reviewer must select one of three decisions:

- **Accept**: Select **Accept** to indicate that the reviewer agrees with the diagnosis.
- **Edit**: Select **Edit** to make the root cause editable, allowing the reviewer to correct or refine the diagnosis before submitting.
- **Reject**: Select **Reject** to indicate that the reviewer does not approve the diagnosis. Rejected diagnoses must not proceed as approved troubleshooting results.

### Step 6 — Add Reviewer Notes

The reviewer may enter additional information in the **Reviewer Notes** field.

Examples:
- *"Diagnosis matches the rule checker finding."*
- *"Root cause was correct, but the recommended next command was changed."*
- *"Diagnosis does not contain sufficient evidence."*

Reviewer notes provide additional audit information.

### Step 7 — Submit the Review

Select **Submit Review**. The frontend sends the review to `POST /api/review`.

The backend records the review decision and performs verification.

---

## Verification Results

The verification section displays the resulting status. Possible states include:
- **Pending**
- **Approved**
- **Blocked**

### Accepted Diagnosis
An accepted diagnosis can proceed to verification.
- **Expected result**: `Approved`

### Edited Diagnosis
An edited diagnosis can also proceed to verification after the reviewer submits the corrected result.
- **Expected result**: `Approved`

### Rejected Diagnosis
A rejected diagnosis is blocked.
- **Expected result**: `Blocked`

This demonstrates that human review is part of the decision workflow rather than an optional display element.

---

## Suggested Demo Case

A useful demonstration case is an **incorrect default gateway**.

### Example Evidence:
- **PC IP**: `192.168.10.25`
- **Subnet Mask**: `255.255.255.0`
- **Gateway**: `192.168.20.1`

The rule checker can identify that the gateway is outside the PC's local subnet.

### Workflow Sequence:
$$	ext{Network Evidence} \longrightarrow 	ext{Rule Checker} \longrightarrow 	ext{AI Diagnosis} \longrightarrow 	ext{Human Review} \longrightarrow 	ext{Verification}$$

The AI may provide additional evidence, troubleshooting commands, and recommended corrective steps. The deterministic checker finding remains authoritative for the root cause.

---

## Demonstrating Human Editing

To demonstrate the Human-in-the-Loop functionality:

1. Select a case.
2. Run diagnosis.
3. Select **Edit**.
4. Modify the root cause.
5. Add reviewer notes.
6. Submit the review.
7. Observe the verification result.

This demonstrates that the human reviewer can modify the AI recommendation before it becomes an approved result.

---

## Demonstrating Rejection

To demonstrate rejection handling:

1. Select a case.
2. Run diagnosis.
3. Select **Reject**.
4. Add a reviewer note explaining the rejection.
5. Submit the review.
6. Observe the verification section.

The verification result should indicate **Blocked**. This demonstrates that an AI-generated recommendation cannot automatically become an approved troubleshooting result.

---

## Backend API Demonstration

The backend exposes the following primary endpoints:

### 1. Health Check
- **Endpoint**: `GET /api/health`
- **Purpose**: Verify that the NetSage backend is running.

### 2. Diagnosis
- **Endpoint**: `POST /api/diagnose`
- **Purpose**: Run the network checker and generate an AI-assisted diagnosis.
- **Input**: Case information, network configuration.
- **Output**: Case ID, checker findings, AI response.

### 3. Review
- **Endpoint**: `POST /api/review`
- **Purpose**: Record the human review decision and perform verification.
- **Input**: Case, AI response, review decision, final root cause, reviewer notes.
- **Output**: Case ID, AI response, review result, verification result.

---

## Audit Logs

NetSage stores workflow information in the `logs/` directory:
- `logs/review_log.csv`
- `logs/verification_log.csv`

These files provide a record of human review and verification results. The demonstration should show that submitting a review produces corresponding log entries.

---

## Test Verification

Before presenting the project, run:

```powershell
python -m pytest
```

All tests should pass. The tests currently cover areas including:
- AI response validation
- Application endpoints
- Checker rules
- Human review
- Rejection handling
- Verification

A successful test run provides additional evidence that the implemented workflow is functioning as expected.

---

## Recommended Demonstration Order

For a short project presentation, use this order:

1. Introduce NetSage AI and explain that it is an AI-assisted Cisco troubleshooting system.
2. Select a troubleshooting case and show the network evidence.
3. Run the diagnosis.
4. Explain the rule checker finding and show the AI diagnosis (confidence, evidence, recommended diagnostic command).
5. Demonstrate human review by accepting or editing the diagnosis.
6. Submit the review and show the verification result.
7. Demonstrate rejection using a second run if time permits.
8. Show the review and verification logs.
9. Run the test suite and show that all tests pass.

---

## Key Demonstration Points

The demonstration should establish that NetSage AI:

- Accepts structured network troubleshooting cases.
- Uses deterministic network checks.
- Uses AI to enrich troubleshooting analysis.
- Validates AI output before returning it.
- Falls back to deterministic results when necessary.
- Provides evidence for the diagnosis.
- Identifies a relevant OSI layer.
- Recommends a diagnostic command.
- Provides recommended corrective steps.
- Does not automatically modify network configurations.
- Requires human review.
- Allows the reviewer to accept, edit, or reject the diagnosis.
- Blocks rejected diagnoses from verification approval.
- Records review and verification results.
- Includes automated tests for core functionality.

---

## Demonstration Architecture

```
+-------------------+
|     Frontend      |
|    NetSage UI     |
+---------+---------+
          |
          | HTTP
          v
+-------------------+
|   Flask Backend   |
+---------+---------+
          |
          +--------------------+
          |                    |
          v                    v
+-------------------+   +-------------------+
|   Rule Checker    |   |    AI Service     |
|   Deterministic   |   |    Gemini API     |
+---------+---------+   +---------+---------+
          |                    |
          +-----------+--------+
                      |
                      v
              +---------------+
              | Human Review  |
              +-------+-------+
                      |
                      v
              +---------------+
              | Verification  |
              +-------+-------+
                      |
                      v
              +---------------+
              |     Logs      |
              +---------------+
```

The important architectural principle demonstrated by the workflow is:

$$\text{AI Recommendation} \longrightarrow \text{Human Review} \longrightarrow \text{Verification}$$

rather than:

$$\text{AI Recommendation} \longrightarrow \text{Automatic Approval}$$

---

## Demo Completion Criteria

The demonstration is considered successful when the following can be shown:

- A case can be selected.
- Network evidence can be entered or displayed.
- Diagnosis can be requested.
- Checker findings are produced.
- An AI response is displayed when the AI service is available.
- Deterministic fallback works when the AI service is unavailable.
- The diagnosis can be accepted.
- The diagnosis can be edited.
- The diagnosis can be rejected.
- Reviewer notes can be submitted.
- Verification produces the correct state.
- Review and verification results are logged.
- The automated test suite passes.