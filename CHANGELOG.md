# Changelog

All notable changes to NetSage AI are documented in this file.

## Unreleased

### Added

- Project README with setup, architecture, workflow, demo, API, testing, and safety guidance.
- Responsible AI documentation describing human review, verification, deterministic safeguards, AI fallback, and responsible-use limitations.

### Changed

- Improved the frontend dashboard to clearly separate AI recommendations, human review decisions, and verification results.
- Added frontend loading, validation, reset, and error states for the troubleshooting workflow.

## 1.0.0

### Added

- Flask API for network diagnosis, human review, and verification.
- Cisco-style troubleshooting case library.
- Deterministic rule checker for gateway, subnet mask, VLAN, interface, and route conditions.
- Gemini-powered diagnosis through an OpenAI-compatible API configuration.
- Structured AI responses containing root cause, confidence, evidence, OSI layer, next command, and fix steps.
- Deterministic diagnosis fallback when Gemini is unavailable or returns an invalid response.
- Human review decisions: Accepted, Edited, and Rejected.
- Verification that approves accepted or edited reviews and blocks rejected diagnoses.
- CSV audit logs for review and verification results.
- Automated tests for checker, AI service, review, verification, full workflow, and rejection handling.