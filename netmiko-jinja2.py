import os
from copy import deepcopy
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from netmiko import ConnectHandler

PRIVATE_KEY = r"C:/Users/LAB308_XX/Desktop/67070085/IPA/PrivateKey"

COMMON_DEVICE = {
    "device_type": "cisco_ios",
    "username": "admin",
    "use_keys": True,
    "key_file": PRIVATE_KEY,
    # "look_for_keys": False,
    # "allow_agent": False,
    "disabled_algorithms": {
        "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
    },
}

devices = [
    {**COMMON_DEVICE, "name": "R0", "host": "172.31.117.1", "template": "router.j2"},
    {**COMMON_DEVICE, "name": "S0-P", "host": "172.31.117.2", "template": "switch.j2"},
    {**COMMON_DEVICE, "name": "S1-P", "host": "172.31.117.3", "template": "switch.j2"},
    {**COMMON_DEVICE, "name": "R1-P", "host": "172.31.117.4", "template": "router.j2"},
    {**COMMON_DEVICE, "name": "R2-P", "host": "172.31.117.5", "template": "router.j2"},
]

config_vars = {
    "S1-P": {
        "vlan_id": 99,
        "vlan_name": "Management",
        "access_interfaces": ["GigabitEthernet0/0"],
        "svi_address": "172.31.117.3 255.255.255.240",
        "default_gateway": "172.31.117.1",
    },
    "R1-P": {
        "vrfs": [
            {"name": "control-data", "rd": "117:2"},
            {"name": "management", "rd": "117:1"},
        ],
        "interfaces": [
            {
                "name": "GigabitEthernet0/0",
                "vrf": "management",
                "address": "172.31.117.4 255.255.255.240",
                "nat": None,
            },
            {
                "name": "GigabitEthernet0/1",
                "vrf": "control-data",
                "address": "10.117.1.1 255.255.255.0",
                "nat": None,
            },
            {
                "name": "GigabitEthernet0/2",
                "vrf": "control-data",
                "address": "10.117.12.1 255.255.255.252",
                "nat": None,
            },
        ],
        "ospf_processes": [
            {
                "process": 10,
                "vrf": "control-data",
                "networks": [
                    {"network": "10.117.1.1", "wildcard": "0.0.0.0", "area": 0},
                    {"network": "10.117.12.1", "wildcard": "0.0.0.0", "area": 0},
                ],
                "default_information": None,
            },
            {
                "process": 20,
                "vrf": "management",
                "networks": [
                    {"network": "172.31.117.0", "wildcard": "0.0.0.15", "area": 15}
                ],
                "default_information": None,
            },
        ],
        "static_routes": [
            "ip route vrf management 0.0.0.0 0.0.0.0 172.31.117.1"
        ],
        "nat_rule": None,
        "acls": [],
        "dns": None,
    },
    "R2-P": {
        "vrfs": [
            {"name": "control-data", "rd": "117:2"},
            {"name": "management", "rd": "117:1"},
        ],
        "interfaces": [
            {
                "name": "GigabitEthernet0/0",
                "vrf": "management",
                "address": "172.31.117.5 255.255.255.240",
                "nat": None,
            },
            {
                "name": "GigabitEthernet0/1",
                "vrf": "control-data",
                "address": "10.117.12.2 255.255.255.252",
                "nat": "inside",
            },
            {
                "name": "GigabitEthernet0/2",
                "vrf": "control-data",
                "address": "10.117.2.1 255.255.255.0",
                "nat": "inside",
            },
            {
                "name": "GigabitEthernet0/3",
                "vrf": "control-data",
                "address": "dhcp",
                "nat": "outside",
            },
        ],
        "ospf_processes": [
            {
                "process": 10,
                "vrf": "control-data",
                # คงค่าตาม running-config ที่ผู้ใช้ส่งมา
                "networks": [
                    {"network": "10.117.1.0", "wildcard": "0.0.0.0", "area": 15},
                    {"network": "10.117.12.0", "wildcard": "0.0.0.0", "area": 15},
                ],
                "default_information": None,
            },
            {
                "process": 20,
                "vrf": "management",
                "networks": [
                    {"network": "172.31.117.0", "wildcard": "0.0.0.15", "area": 15}
                ],
                "default_information": None,
            },
        ],
        "static_routes": [
            "ip route vrf management 0.0.0.0 0.0.0.0 172.31.117.1",
            "ip route vrf control-data 0.0.0.0 0.0.0.0 dhcp",
        ],
        "nat_rule": "ip nat inside source list 10 interface GigabitEthernet0/3 vrf control-data overload",
        "acls": ["access-list 10 permit any"],
        "dns": None,
    },
}

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_commands(device_name: str, template_name: str) -> list[str]:
    """Render configuration commands for one device."""
    template = jinja_env.get_template(template_name)
    rendered = template.render(**config_vars[device_name])
    return [line.strip() for line in rendered.splitlines() if line.strip()]


def main() -> None:
    for device in devices:
        dev = deepcopy(device)
        dev_name = dev.pop("name")
        template_name = dev.pop("template")
        net_connect = None

        try:
            commands = render_commands(dev_name, template_name)
            print(f"--- Connecting to {dev_name} ({dev['host']}) ---")

            net_connect = ConnectHandler(**dev)
            net_connect.enable()

            print(f"Applying configuration to {dev_name}...")
            output = net_connect.send_config_set(commands)
            print(output)

            print(net_connect.save_config())
            print(f"--- Completed {dev_name} successfully ---\n")

        except Exception as error:
            print(f"Failed to configure {dev_name}: {error}\n")

        finally:
            if net_connect is not None:
                net_connect.disconnect()


if __name__ == "__main__":
    main()
