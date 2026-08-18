def check_gateway(ip, mask, gateway):
    if not ip or not mask or not gateway:
        return None

    ip_parts = ip.split(".")
    gateway_parts = gateway.split(".")

    if mask == "255.255.255.0":
        if ip_parts[:3] != gateway_parts[:3]:
            return "Gateway is outside the local subnet"

    return None


def check_mask(ip, mask):
    if not ip or not mask:
        return None

    if mask not in ["255.255.255.0", "255.255.255.252"]:
        return "Unsupported or unexpected subnet mask"

    return None


def check_vlan(vlan, existing_vlans, interface_vlan=None):
    if vlan is None or existing_vlans is None:
        return None

    if vlan not in existing_vlans:
        return "Required VLAN is missing"

    if interface_vlan is not None and interface_vlan != vlan:
        return "Interface is assigned to the wrong VLAN"

    return None


def check_interface(status):
    if status is None:
        return None

    if status.lower() != "up":
        return "Interface is down"

    return None


def check_route(network, routes):
    if network is None or routes is None:
        return None

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

    if "vlan" in data and "existing_vlans" in data:
        result = check_vlan(
            data.get("vlan"),
            data.get("existing_vlans"),
            data.get("interface_vlan")
        )
        if result:
            findings.append(result)

    if "interface_status" in data:
        result = check_interface(
            data.get("interface_status")
        )
        if result:
            findings.append(result)

    if "required_network" in data and "routes" in data:
        result = check_route(
            data.get("required_network"),
            data.get("routes")
        )
        if result:
            findings.append(result)

    return findings