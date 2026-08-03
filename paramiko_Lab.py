import paramiko

devices = [
    {"host": "172.31.117.1", "name": "R0"},
    {"host": "172.31.117.4", "name": "R1"},
    {"host": "172.31.117.5", "name": "R2"},
    {"host": "172.31.117.2", "name": "S0"},
    {"host": "172.31.117.3", "name": "S1"},
]

username = "admin"
pkey_path = "C:/Users/LAB308_XX/Desktop/67070085/ipa/PrivateKey"

key = paramiko.RSAKey.from_private_key_file(pkey_path)

for dev in devices:
    print(f"Connecting to {dev['name']} ({dev['host']})...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=dev["host"],
            username=username,
            pkey=key,
            look_for_keys=False,
            allow_agent=False,
            disabled_algorithms={
                "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]
            }
        )

        print(f"Successfully SSH to {dev['name']}")

        if dev["name"] == "R0":
            stdin, stdout, stderr = client.exec_command(
                "show running-config"
            )

            output = stdout.read().decode("utf-8")

            with open("R0-running.cfg", "w", encoding="utf-8") as f:
                f.write(output)

            print("Saved R0 running-config to R0-running.cfg")

    except Exception as e:
        print(f"Failed to connect to {dev['name']}: {e}")

    finally:
        client.close()