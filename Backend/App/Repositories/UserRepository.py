import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class UserRepository:
    def __init__(self):
        """Initialize the UserRepository with a SQLite database path."""
        self.db_path = 'clients.db'
        self._initialize_db()

    def _initialize_db(self):
        """Create the users table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            conn.commit()

    def create_user(self, username, password) -> bool:
        """Create a new user with a hashed password."""
        hashed_password = generate_password_hash(password)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                ''', (username, hashed_password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False


    def confirm_user(self, username, password) -> bool:
        """Confirm a user's credentials by checking the hashed password."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password_hash FROM users
                WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()

        if row is None:
            return False  # User not found

        stored_password_hash = row[0]
        return check_password_hash(stored_password_hash, password)
