# NetSage AI Case Schema

Each troubleshooting case contains the network symptom, available evidence, expected diagnosis, and expected fix.

## Fields

| Field | Description |
|---|---|
| case_id | Unique ID for the troubleshooting case. |
| concept | Main networking concept involved. |
| severity | Severity of the network problem. |
| symptom | Problem observed by the user. |
| topology | Relevant Packet Tracer topology information. |
| show_output | Cisco show command output available for diagnosis. |
| expected_fault | Ground-truth root cause of the problem. |
| osi_layer | Main OSI layer related to the fault. |
| expected_next_command | Command that should be run next to investigate the problem. |
| expected_fix | Correct configuration or troubleshooting action. |

## Allowed Severity Values

- Low
- Medium
- High
- Critical

## Common Concept Values

- VLAN
- Default Gateway
- DHCP
- DNS
- Static Routing
- Dynamic Routing
- ACL
- NAT
- Wireless

## OSI Layer Format

Use the following format:

- Layer 1
- Layer 2
- Layer 3
- Layer 4
- Layer 7

If a problem involves multiple layers, use:

`Layer 2 / Layer 3`

## Example

```text
Case ID: NET-001

Concept: VLAN

Severity: Medium

Symptom:
PC1 cannot ping PC2.

Topology:
PC1 -> SW1 -> PC2

Show Output:
show vlan brief

Expected Fault:
PC2 is assigned to the wrong VLAN.

OSI Layer:
Layer 2

Expected Next Command:
show interfaces fa0/2 switchport

Expected Fix:
Assign Fa0/2 to the correct VLAN.