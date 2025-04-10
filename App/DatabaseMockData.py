import sqlite3
import uuid
import json
import random
from werkzeug.security import generate_password_hash, check_password_hash

# Utility functions
def random_mac_address():
    return ":".join("{:02X}".format(random.randint(0, 255)) for _ in range(6))

def random_ip_address():
    return f"192.168.1.{random.randint(2, 254)}"

def random_storage():
    used = random.randint(10, 100)
    total = random.choice([128, 256, 512])
    return f"{used}/{total}"

def sample_firewall_status():
    status = {
        "Domain": random.choice([True, False]),
        "Private": random.choice([True, False]),
        "Public": random.choice([True, False])
    }
    return json.dumps(status)

def sample_bitlocker_status():
    statuses = [
        {
            "DeviceID": "C:",
            "ProtectionStatus": random.choice(["On (Protected)", "Off (Not Protected)"]),
            "EncryptionMethod": random.choice(["XTS-AES 256-bit", "AES 128-bit"])
        },
        {
            "DeviceID": "D:",
            "ProtectionStatus": random.choice(["On (Protected)", "Off (Not Protected)"]),
            "EncryptionMethod": random.choice(["XTS-AES 256-bit", "AES 128-bit"])
        }
    ]
    return json.dumps(statuses)

def sample_windows_version():
    version = random.choice(["10", "11"])
    version_number = random.choice(["10.0.19042", "10.0.22000", "10.0.18363"])
    return version, version_number

def sample_installed_programs():
    software_options = [
        ("Chrome", "95.0", "96.0"),
        ("Firefox", "89.0", "90.0"),
        ("Office", "2019", "2021"),
        ("Slack", "4.20", "4.25"),
        ("Zoom", "5.6", "5.7")
    ]
    return random.sample(software_options, 2)

def add_admin_user(cursor):
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        username = "admin"
        password = "test"

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_password)
        )

def add_mock_data():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()

    # Insert clients without sites
    for i in range(1, 6):  # 5 clients
        client_uuid = str(uuid.uuid4())
        client_mac = random_mac_address()
        client_nickname = f"Client {i}"
        shutdown = random.choice([0, 1])
        storage = random_storage()
        firewall_status = sample_firewall_status()
        windows_version, windows_version_number = sample_windows_version()
        bitlocker_status = sample_bitlocker_status()
        current_user = f"User_{i}"

        cursor.execute('''
            INSERT INTO clients (
                uuid, mac_address, nickname, shutdown, storage, 
                firewall_status, windows_version, windows_version_number, 
                bitlocker_status, current_user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_uuid, client_mac, client_nickname, shutdown, storage,
            firewall_status, windows_version, windows_version_number,
            bitlocker_status, current_user
        ))
        print(f"Inserted client {client_nickname}")

        # Insert installed programs for this client
        programs = sample_installed_programs()
        for name, current_version, available_version in programs:
            cursor.execute('''
                INSERT INTO installed_programs (client_uuid, name, current_version, available_version)
                VALUES (?, ?, ?, ?)
            ''', (client_uuid, name, current_version, available_version))
            print(f"  Inserted program {name} for {client_nickname}")

    add_admin_user(cursor)

    conn.commit()
    conn.close()
    print("Mock data insertion complete.")

if __name__ == "__main__":
    add_mock_data()
