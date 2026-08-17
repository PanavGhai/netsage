# NetSage AI Dashboard Specification

## Purpose

The NetSage AI dashboard provides a single interface for network troubleshooting cases, AI-assisted diagnosis, human review, and verification.

The dashboard must make the complete troubleshooting workflow visible to the user.

## Dashboard Workflow

1. Select a troubleshooting case.
2. Review the case symptoms and topology.
3. Review available network configuration and command output.
4. Run the diagnosis.
5. Display the AI diagnosis.
6. Display confidence and supporting evidence.
7. Display the relevant OSI layer.
8. Display the next diagnostic command.
9. Display recommended fix steps.
10. Require human review.
11. Allow the reviewer to Accept, Edit, or Reject the diagnosis.
12. Record reviewer notes.
13. Submit the review.
14. Display verification status.
15. Preserve the review and verification result in the backend logs.

## Dashboard Sections

### Case

Displays:

- Case ID
- Case concept
- Symptoms
- Topology
- Show command output
- IP address
- Subnet mask
- Default gateway

### AI Diagnosis

Displays:

- Root cause
- Confidence
- OSI layer
- Evidence
- Next diagnostic command
- Recommended fix steps

The dashboard must clearly distinguish an AI recommendation from an approved diagnosis.

### Human Review

Provides:

- Accept button
- Edit button
- Reject button
- Editable root cause when Edit is selected
- Reviewer notes
- Submit Review button
- Review status

A diagnosis must not be considered approved solely because the AI generated it.

### Verification

Displays:

- Verification status
- Verification message

Possible verification states include:

- Pending
- Approved
- Blocked

### Human-in-the-Loop Requirement

Every AI diagnosis must pass through human review.

Accepted and edited diagnoses may proceed to verification.

Rejected diagnoses must be blocked.

## Safety Requirements

The dashboard must not imply that an AI recommendation has automatically changed a network configuration.

Fix steps are recommendations only.

The dashboard must clearly distinguish:

- AI-generated diagnosis
- Human-edited diagnosis
- Human approval
- Verification result

## Error Handling

The dashboard must display an appropriate error when:

- A case has not been selected.
- Diagnosis fails.
- The backend cannot be reached.
- Review submission fails.

## Backend Integration

Diagnosis:

`POST /api/diagnose`

Review:

`POST /api/review`

Case data:

`/data/cases.json`

## Auditability

Review and verification results are recorded by the backend.

The frontend should display the resulting verification state after review submission.