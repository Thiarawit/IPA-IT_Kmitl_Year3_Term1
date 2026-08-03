from netmiko import ConnectHandler

USERNAME = "admin"
PRIVATE_KEY = r"C:/Users/LAB308_XX/Desktop/67070085/IPA/PrivateKey"

DEVICES = {
    "R1-P": "172.31.117.4",
    "R2-P": "172.31.117.5",
    "S1-P": "172.31.117.3",
}

DESCRIPTIONS = {
    "R1-P": {
        "GigabitEthernet0/1": "Connect to PC",
        "GigabitEthernet0/2": "Connect to G0/1 of R2",
    },
    "R2-P": {
        "GigabitEthernet0/1": "Connect to G0/2 of R1",
        "GigabitEthernet0/2": "Connect to G0/1 of S1",
        "GigabitEthernet0/3": "Connect to WAN",
    },
    "S1-P": {
        "GigabitEthernet0/1": "Connect to G0/2 of R2",
        "GigabitEthernet1/1": "Connect to PC",
    },
}


def apply_descriptions():
    for name, host in DEVICES.items():
        print(f"Connecting to {name} ({host})...")

        device = {
            "device_type": "cisco_ios",
            "host": host,
            "username": USERNAME,
            "use_keys": True,
            "key_file": PRIVATE_KEY,
            "disabled_algorithms": {
                "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
            },
        }

        conn = None

        try:
            conn = ConnectHandler(**device)
            conn.enable()

            commands = []

            for interface, description in DESCRIPTIONS[name].items():
                commands.extend([
                    f"interface {interface}",
                    f"description {description}",
                    "exit",
                ])

            print(conn.send_config_set(commands))
            print(conn.save_config())

            print(f"{name} configured successfully.\n")

        except Exception as e:
            print(f"Failed to configure {name}: {e}\n")

        finally:
            if conn:
                conn.disconnect()


if __name__ == "__main__":
    apply_descriptions()