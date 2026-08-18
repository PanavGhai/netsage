from checker.rules import run_checks


def test_gateway_check():
    data = {
        "ip": "192.168.10.25",
        "mask": "255.255.255.0",
        "gateway": "192.168.20.1"
    }

    findings = run_checks(data)

    assert "Gateway is outside the local subnet" in findings


def test_vlan_check():
    data = {
        "vlan": "20",
        "existing_vlans": ["10", "30"]
    }

    findings = run_checks(data)

    assert "Required VLAN is missing" in findings


def test_interface_check():
    data = {
        "interface_status": "down"
    }

    findings = run_checks(data)

    assert "Interface is down" in findings


def test_route_check():
    data = {
        "required_network": "192.168.30.0/24",
        "routes": ["192.168.10.0/24"]
    }

    findings = run_checks(data)

    assert "Route to network is missing" in findings

def test_wrong_vlan_assignment():
    data = {
        "vlan": "10",
        "existing_vlans": ["10", "20"],
        "interface_vlan": "20"
    }

    findings = run_checks(data)

    assert "Interface is assigned to the wrong VLAN" in findings