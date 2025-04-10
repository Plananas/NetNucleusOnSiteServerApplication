import json
import sqlite3
from App import DatabaseMockData
from werkzeug.security import generate_password_hash


def setup_database():
    # Connect to the database (creates a file-based database)
    print("SETTING UP DATABASE")
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()

    # Create a table for clients with a foreign key reference to sites
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

    # Check if the "sites" table is empty (i.e. first run)
    cursor.execute("SELECT COUNT(*) FROM clients")
    row_count = cursor.fetchone()[0]

    # Commit and close the connection before calling addmockData()
    conn.commit()
    conn.close()


    if row_count == 0:
        print("No existing data found. Running mock data insertion...")
        DatabaseMockData.add_mock_data()
    else:
        print("Database already contains data. Skipping mock data insertion.")
