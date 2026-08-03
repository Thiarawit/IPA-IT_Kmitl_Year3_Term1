import pytest
from netmiko import ConnectHandler

USERNAME = "admin"
PRIVATE_KEY = r"C:/Users/LAB308_XX/Desktop/67070085/IPA/PrivateKey"

DEVICES = {
    "S1-P": "172.31.117.3",
    "R1-P": "172.31.117.4",
    "R2-P": "172.31.117.5",
}


def get_descriptions(ip):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": USERNAME,
        "use_keys": True,
        "key_file": PRIVATE_KEY,
        "disabled_algorithms": {
            "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
        },
    }

    conn = ConnectHandler(**device)
    conn.enable()

    output = conn.send_command(
        "show interfaces description",
        use_textfsm=True
    )

    conn.disconnect()

    assert isinstance(output, list), \
        f"TextFSM parsing failed: {output!r}"

    return {
        row["port"]: row["description"]
        for row in output
    }


@pytest.fixture(scope="module")
def s1_descs():
    return get_descriptions(DEVICES["S1-P"])


@pytest.fixture(scope="module")
def r1_descs():
    return get_descriptions(DEVICES["R1-P"])


@pytest.fixture(scope="module")
def r2_descs():
    return get_descriptions(DEVICES["R2-P"])


def test_s1_interfaces(s1_descs):
    assert s1_descs["Gi0/1"] == "Connect to G0/2 of R2"
    assert s1_descs["Gi1/1"] == "Connect to PC"


def test_r1_interfaces(r1_descs):
    assert r1_descs["Gi0/1"] == "Connect to PC"
    assert r1_descs["Gi0/2"] == "Connect to G0/1 of R2"


def test_r2_interfaces(r2_descs):
    assert r2_descs["Gi0/1"] == "Connect to G0/2 of R1"
    assert r2_descs["Gi0/2"] == "Connect to G0/1 of S1"
    assert r2_descs["Gi0/3"] == "Connect to WAN"