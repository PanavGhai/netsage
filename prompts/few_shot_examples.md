# NetSage Few-Shot Examples

## Example 1 — VLAN

Input:

Symptom:
PC1 cannot ping PC2.

Topology:
PC1 -> SW1 -> PC2

Show Output:
show vlan brief:
Fa0/1 VLAN 10
Fa0/2 VLAN 20

Rule Checker:
No deterministic findings.

Expected Output:

{
  "root_cause": "PC2 is assigned to the wrong VLAN",
  "confidence": "High",
  "evidence": [
    "Fa0/1 is assigned to VLAN 10",
    "Fa0/2 is assigned to VLAN 20"
  ],
  "osi_layer": "Layer 2",
  "next_command": "show interfaces fa0/2 switchport",
  "fix_steps": [
    "Verify the intended VLAN for Fa0/2",
    "Assign Fa0/2 to VLAN 10 if VLAN 10 is the intended network"
  ]
}

## Example 2 — Default Gateway

Input:

Symptom:
PC receives an IP address but cannot reach remote networks.

Topology:
PC1 -> SW1 -> R1 -> Server

Show Output:
PC IP: 192.168.10.25
Mask: 255.255.255.0
Gateway: 192.168.20.1

Rule Checker:
Gateway is outside the local subnet.

Expected Output:

{
  "root_cause": "PC1 has an incorrect default gateway",
  "confidence": "High",
  "evidence": [
    "PC1 uses 192.168.10.25/24",
    "The configured gateway is 192.168.20.1",
    "The gateway is outside the 192.168.10.0/24 subnet"
  ],
  "osi_layer": "Layer 3",
  "next_command": "ipconfig /all",
  "fix_steps": [
    "Set the default gateway to the correct gateway for the 192.168.10.0/24 network"
  ]
}

## Example 3 — Missing Route

Input:

Symptom:
PC1 cannot reach the server network.

Topology:
PC1 -> R1 -> R2 -> Server

Show Output:
show ip route:
Connected: 192.168.10.0/24
Connected: 10.0.0.0/30

Rule Checker:
Route to network is missing.

Expected Output:

{
  "root_cause": "R1 does not have a route to the server network",
  "confidence": "High",
  "evidence": [
    "The routing table does not contain the server network",
    "The rule checker reports that the required route is missing"
  ],
  "osi_layer": "Layer 3",
  "next_command": "show ip route",
  "fix_steps": [
    "Add a route to the server network using the correct next hop"
  ]
}