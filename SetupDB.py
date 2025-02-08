import json
import sqlite3

# Connect to the database (creates a file-based database)
conn = sqlite3.connect('../clients.db')
cursor = conn.cursor()

# Create a table for clients
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL UNIQUE,
    mac_address TEXT NOT NULL UNIQUE,
    nickname TEXT,
    shutdown INTEGER NOT NULL, -- Use INTEGER for boolean values
    storage TEXT NOT NULL,
    firewall_status TEXT NOT NULL,
    windows_version TEXT NOT NULL,
    windows_version_number TEXT NOT NULL,
    bitlocker_status TEXT NOT NULL,
    current_user TEXT
)
''')

# Create a table for installed programs with a unique constraint on (client_uuid, name)
cursor.execute('''
CREATE TABLE IF NOT EXISTS installed_programs (
    id INTEGER PRIMARY KEY,
    client_uuid TEXT NOT NULL,
    name TEXT NOT NULL,
    current_version TEXT,
    available_version TEXT,
    FOREIGN KEY(client_uuid) REFERENCES clients(uuid),
    UNIQUE(client_uuid, name)
)
''')

# Create a table for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

# Insert data into installed_programs
cursor.execute('''
INSERT INTO installed_programs (client_uuid, name, current_version) 
VALUES (?, ?, ?)
''', ('123e4567-e89b-12d3-a456-426614174000', 'Test Program', '1.0'))

import json

# Mock data
uuid_value = "123e4567-e89b-12d3-a456-426614174000"
mac_address_value = "00:1A:2B:3C:4D:5E"
nickname_value = "Testing PC"
shutdown_value = 1  # 1 = Offline, 0 = Online
storage_value = "60/128"  # Used 60GB out of 128GB
firewall_status_value = json.dumps({"Domain": True, "Private": True, "Public": False})  # Convert dict to JSON string
windows_version = "11"
windows_version_number = "10.0.26100.3037"
bitlocker_status = json.dumps([
    {
        "DeviceID": "C:",
        "ProtectionStatus": "Off (Not Protected)",
        "EncryptionMethod": "XTS-AES 256-bit"
    },
    {
        "DeviceID": "D:",
        "ProtectionStatus": "On (Protected)",
        "EncryptionMethod": "AES 128-bit"
    }
])

current_user = "Test User"

# Execute insert query
cursor.execute('''
INSERT INTO clients (uuid, mac_address, nickname, shutdown, storage, firewall_status, windows_version, windows_version_number, bitlocker_status, current_user) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (uuid_value, mac_address_value, nickname_value, shutdown_value, storage_value, firewall_status_value, windows_version, windows_version_number, bitlocker_status, current_user))

# Commit and close
conn.commit()
conn.close()
