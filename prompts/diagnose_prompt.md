# NetSage Diagnosis Prompt

Analyze the following network troubleshooting case.

## Symptom

{symptom}

## Topology

{topology}

## Show Command Output

{show_output}

## Rule Checker Findings

{rule_findings}

## Task

Identify the most likely root cause.

Use the available evidence to support the diagnosis.

Recommend one next diagnostic command.

Provide a safe fix recommendation.

Return only valid JSON using this structure:

{
  "root_cause": "",
  "confidence": "",
  "evidence": [],
  "osi_layer": "",
  "next_command": "",
  "fix_steps": []
}

Do not invent evidence.

If the evidence is insufficient, lower the confidence and use the next command to gather more information.

The recommendation is not considered approved until a human reviewer accepts or edits it.