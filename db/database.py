# db/database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="gantt.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
        """)

        # Teams table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)

        # Artisans table (added profile_picture column)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS artisans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team_id INTEGER,
                skill TEXT,
                availability TEXT,
                profile_picture TEXT,  /* Added column for profile picture path */
                FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE SET NULL
            );
        """)

        # Projects table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                job_number TEXT,
                description TEXT
            );
        """)

        # Assignments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artisan_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                FOREIGN KEY(artisan_id) REFERENCES artisans(id) ON DELETE CASCADE,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

    def add_user(self, username, password, role):
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")

    def get_user(self, username, password):
        self.cursor.execute(
            "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = self.cursor.fetchone()
        if user:
            return {"id": user[0], "username": user[1], "role": user[2]}
        return None

    def add_artisan(self, name, team_id=None, skill=None, availability=None, profile_picture=None):
        try:
            self.cursor.execute(
                "INSERT INTO artisans (name, team_id, skill, availability, profile_picture) VALUES (?, ?, ?, ?, ?)",
                (name, team_id, skill, availability, profile_picture)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise ValueError(f"Failed to add artisan: {str(e)}")

    def get_artisans(self):
        return self.cursor.execute("SELECT id, name, team_id, skill, availability, profile_picture FROM artisans").fetchall()

    def add_project(self, name, start_date, end_date, status, job_number=None, description=None):
        try:
            self.cursor.execute(
                "INSERT INTO projects (name, start_date, end_date, status, job_number, description) VALUES (?, ?, ?, ?, ?, ?)",
                (name, start_date, end_date, status, job_number, description)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise ValueError(f"Failed to add project: {str(e)}")

    def get_projects(self):
        return self.cursor.execute("SELECT id, name, start_date, end_date, status, job_number, description FROM projects").fetchall()

    def add_assignment(self, artisan_id, project_id, start_date, end_date):
        try:
            self.cursor.execute(
                "INSERT INTO assignments (artisan_id, project_id, start_date, end_date) VALUES (?, ?, ?, ?)",
                (artisan_id, project_id, start_date, end_date)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise ValueError(f"Failed to add assignment: {str(e)}")

    def get_assignments(self):
        return self.cursor.execute("SELECT id, artisan_id, project_id, start_date, end_date FROM assignments").fetchall()

    def update_assignment(self, assignment_id, start_date, end_date):
        try:
            self.cursor.execute(
                "UPDATE assignments SET start_date = ?, end_date = ? WHERE id = ?",
                (start_date, end_date, assignment_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise ValueError(f"Failed to update assignment: {str(e)}")

    def add_team(self, name):
        try:
            self.cursor.execute("INSERT INTO teams (name) VALUES (?)", (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add team: {str(e)}")

    def update_artisan_team(self, artisan_id, team_id):
        self.cursor.execute("UPDATE artisans SET team_id = ? WHERE id = ?", (team_id, artisan_id))
        self.conn.commit()

    def close(self):
        self.conn.close()