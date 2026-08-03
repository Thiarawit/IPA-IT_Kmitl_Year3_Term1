from copy import deepcopy
from netmiko import ConnectHandler

PRIVATE_KEY = r"C:/Users/LAB308_XX/Desktop/67070085/IPA/PrivateKey"

COMMON_DEVICE = {
    "device_type": "cisco_ios",
    "username": "admin",
    "use_keys": True,
    "key_file": PRIVATE_KEY,
    "disabled_algorithms": {
        "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
    },
}

devices = [
    {**COMMON_DEVICE, "host": "172.31.117.1", "name": "R0"},
    {**COMMON_DEVICE, "host": "172.31.117.2", "name": "S0-P"},
    {**COMMON_DEVICE, "host": "172.31.117.3", "name": "S1-P"},
    {**COMMON_DEVICE, "host": "172.31.117.4", "name": "R1-P"},
    {**COMMON_DEVICE, "host": "172.31.117.5", "name": "R2-P"},
]

r0 = [
    "router ospf 10 vrf management",
    "network 172.31.117.0 0.0.0.15 area 15",
    "default-information originate",
    "exit",
    "access-list 10 permit 172.31.117.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 4",
    "access-class 10 in",
]

s0 = [
    "vlan 99",
    "name Management",
    "exit",
    "interface range GigabitEthernet0/0 - 3",
    "switchport mode access",
    "switchport access vlan 99",
    "no shutdown",
    "exit",
    "access-list 10 permit 172.31.117.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 4",
    "access-class 10 in",
]

s1 = [
    "vlan 101",
    "name Control-Data",
    "exit",
    "interface GigabitEthernet0/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
    "exit",
    "interface GigabitEthernet1/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
    "exit",
    "access-list 10 permit 172.31.117.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 4",
    "access-class 10 in",
]

r1 = [
    "router ospf 20 vrf management",
    "network 172.31.117.0 0.0.0.15 area 15",
    "exit",
    "router ospf 10 vrf control-data",
    "network 10.117.1.1 0.0.0.0 area 0",
    "network 10.117.12.1 0.0.0.0 area 0",
    "exit",
    "ip route vrf management 0.0.0.0 0.0.0.0 172.31.117.1",
    "access-list 10 permit 172.31.117.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 4",
    "access-class 10 in",
]

r2 = [
    "router ospf 20 vrf management",
    "network 172.31.117.0 0.0.0.15 area 15",
    "exit",
    "router ospf 10 vrf control-data",
    "network 10.117.12.2 0.0.0.0 area 0",
    "network 10.117.2.1 0.0.0.0 area 0",
    "default-information originate always",
    "exit",
    "ip route vrf management 0.0.0.0 0.0.0.0 172.31.117.1",
    "ip route vrf control-data 0.0.0.0 0.0.0.0 dhcp",
    "interface GigabitEthernet0/1",
    "ip nat inside",
    "exit",
    "interface GigabitEthernet0/2",
    "ip nat inside",
    "exit",
    "interface GigabitEthernet0/3",
    "ip nat outside",
    "exit",
    "access-list 1 permit 10.117.0.0 0.0.255.255",
    "ip nat inside source list 1 interface GigabitEthernet0/3 vrf control-data overload",
    "access-list 10 permit 172.31.117.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 4",
    "access-class 10 in",
    "exit",
    "ip dns server",
    "ip domain lookup",
    "ip name-server vrf control-data 192.168.42.1",
    "ip name-server vrf control-data 8.8.8.8",
    "ip name-server vrf control-data 1.1.1.1",
]

config_map = {
    "R0": r0,
    "S0-P": s0,
    "S1-P": s1,
    "R1-P": r1,
    "R2-P": r2,
}


def main():
    for device in devices:
        dev = deepcopy(device)
        dev_name = dev.pop("name")

        print(f"--- Connecting to {dev_name} ({dev['host']}) ---")
        net_connect = None

        try:
            net_connect = ConnectHandler(**dev)
            net_connect.enable()

            print(f"Applying configurations to {dev_name}...")
            output = net_connect.send_config_set(config_map[dev_name])
            print(output)

            save_output = net_connect.save_config()
            print(save_output)
            print(f"--- Completed {dev_name} successfully ---\n")

        except Exception as error:
            print(f"Failed to configure {dev_name}: {error}\n")

        finally:
            if net_connect is not None:
                net_connect.disconnect()


if __name__ == "__main__":
    main()