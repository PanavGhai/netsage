def check_gateway(ip, mask, gateway):
    if not ip or not mask or not gateway:
        return "Missing IP, mask, or gateway"

    ip_parts = ip.split(".")
    gateway_parts = gateway.split(".")

    if mask == "255.255.255.0":
        if ip_parts[:3] != gateway_parts[:3]:
            return "Gateway is outside the local subnet"

    return None


def check_mask(ip, mask):
    if not ip or not mask:
        return "Missing IP or subnet mask"

    if mask not in ["255.255.255.0", "255.255.255.252"]:
        return "Unsupported or unexpected subnet mask"

    return None


def check_vlan(vlan, existing_vlans):
    if vlan not in existing_vlans:
        return "Required VLAN is missing"

    return None


def check_interface(status):
    if status.lower() != "up":
        return "Interface is down"

    return None


def check_route(network, routes):
    if network not in routes:
        return "Route to network is missing"

    return None


def run_checks(data):
    findings = []

    result = check_gateway(
        data.get("ip"),
        data.get("mask"),
        data.get("gateway")
    )
    if result:
        findings.append(result)

    result = check_mask(
        data.get("ip"),
        data.get("mask")
    )
    if result:
        findings.append(result)

    result = check_vlan(
        data.get("vlan"),
        data.get("existing_vlans", [])
    )
    if result:
        findings.append(result)

    result = check_interface(
        data.get("interface_status", "down")
    )
    if result:
        findings.append(result)

    result = check_route(
        data.get("required_network"),
        data.get("routes", [])
    )
    if result:
        findings.append(result)

    return findings