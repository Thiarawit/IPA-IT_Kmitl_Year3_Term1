import re
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
    {**COMMON_DEVICE, "name": "R1-P", "host": "172.31.117.4"},
    {**COMMON_DEVICE, "name": "R2-P", "host": "172.31.117.5"},
]

ACTIVE_INTERFACE_RE = re.compile(
    r"^(\S+)\s+(\S+)\s+\S+\s+\S+\s+up\s+up",
    re.MULTILINE,
)

UPTIME_RE = re.compile(
    r"^(\S+)\s+uptime is\s+(.+)$",
    re.MULTILINE,
)


def get_active_interfaces(output):
    return ACTIVE_INTERFACE_RE.findall(output)


def get_uptime(output):
    match = UPTIME_RE.search(output)
    return match.group(2) if match else "Unknown"


def main():

    for device in devices:

        dev = device.copy()
        name = dev.pop("name")

        print("=" * 60)
        print(f"Connecting to {name} ({dev['host']})")

        connection = None

        try:
            connection = ConnectHandler(**dev)
            connection.enable()

            interface_output = connection.send_command("show ip interface brief")
            version_output = connection.send_command("show version")

            uptime = get_uptime(version_output)
            interfaces = get_active_interfaces(interface_output)

            print(f"\n{name}")
            print(f"Router Uptime : {uptime}\n")

            if interfaces:
                print(f"{'Interface':<25}{'IP Address'}")
                print("-" * 40)

                for interface, ip in interfaces:
                    print(f"{interface:<25}{ip}")
            else:
                print("No active interfaces found.")

            print()

        except Exception as e:
            print(f"Failed to connect to {name}: {e}")

        finally:
            if connection:
                connection.disconnect()


if __name__ == "__main__":
    main()