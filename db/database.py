# db/database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="gantt.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Projects table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                job_number TEXT,
                description TEXT
            )
        ''')

        # Artisans table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS artisans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                skill TEXT,
                availability TEXT,
                profile_picture TEXT,
                team_id INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')

        # Teams table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Assignments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artisan_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                FOREIGN KEY (artisan_id) REFERENCES artisans(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        # Activity Log table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        self.conn.commit()

        # Ensure the default user exists
        self.ensure_default_user()

    def ensure_default_user(self):
        # Check if the default user 'cm_user' exists, if not, create it
        self.cursor.execute("SELECT * FROM users WHERE username = ?", ("cm_user",))
        if not self.cursor.fetchone():
            self.add_user("cm_user", "pass123")

    def add_user(self, username, password):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, password))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")

    def get_user(self, username, password):
        self.cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        user = self.cursor.fetchone()
        if user:
            return {"id": user[0], "username": user[1]}
        return None

    def add_project(self, name, start_date, end_date, status, job_number, description):
        self.cursor.execute('''
            INSERT INTO projects (name, start_date, end_date, status, job_number, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, start_date, end_date, status, job_number, description))
        project_id = self.cursor.lastrowid
        self.conn.commit()
        # Log the activity
        self.log_activity("Project Added", f"Project '{name}' (ID: {project_id}) added")
        return project_id

    def add_artisan(self, name, skill, availability, profile_picture=None):
        self.cursor.execute('''
            INSERT INTO artisans (name, skill, availability, profile_picture)
            VALUES (?, ?, ?, ?)
        ''', (name, skill, availability, profile_picture))
        artisan_id = self.cursor.lastrowid
        self.conn.commit()
        # Log the activity
        self.log_activity("Artisan Added", f"Artisan '{name}' (ID: {artisan_id}) added")
        return artisan_id

    def add_team(self, name):
        self.cursor.execute('''
            INSERT INTO teams (name) VALUES (?)
        ''', (name,))
        team_id = self.cursor.lastrowid
        self.conn.commit()
        # Log the activity
        self.log_activity("Team Added", f"Team '{name}' (ID: {team_id}) added")
        return team_id

    def add_assignment(self, artisan_id, project_id, start_date, end_date):
        self.cursor.execute('''
            INSERT INTO assignments (artisan_id, project_id, start_date, end_date)
            VALUES (?, ?, ?, ?)
        ''', (artisan_id, project_id, start_date, end_date))
        assignment_id = self.cursor.lastrowid
        self.conn.commit()
        # Log the activity
        project = self.cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,)).fetchone()
        artisan = self.cursor.execute("SELECT name FROM artisans WHERE id = ?", (artisan_id,)).fetchone()
        self.log_activity("Assignment Added", f"Artisan '{artisan[0]}' assigned to project '{project[0]}' (Assignment ID: {assignment_id})")
        return assignment_id

    def update_assignment(self, assignment_id, start_date, end_date):
        self.cursor.execute('''
            UPDATE assignments SET start_date = ?, end_date = ?
            WHERE id = ?
        ''', (start_date, end_date, assignment_id))
        self.conn.commit()
        # Log the activity
        assignment = self.cursor.execute("SELECT artisan_id, project_id FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
        project = self.cursor.execute("SELECT name FROM projects WHERE id = ?", (assignment[1],)).fetchone()
        artisan = self.cursor.execute("SELECT name FROM artisans WHERE id = ?", (assignment[0],)).fetchone()
        self.log_activity("Assignment Updated", f"Assignment for artisan '{artisan[0]}' on project '{project[0]}' updated (ID: {assignment_id})")

    def update_artisan_team(self, artisan_id, team_id):
        self.cursor.execute('''
            UPDATE artisans SET team_id = ? WHERE id = ?
        ''', (team_id, artisan_id))
        self.conn.commit()
        # Log the activity
        artisan = self.cursor.execute("SELECT name FROM artisans WHERE id = ?", (artisan_id,)).fetchone()
        team = self.cursor.execute("SELECT name FROM teams WHERE id = ?", (team_id,)).fetchone()
        self.log_activity("Artisan Team Updated", f"Artisan '{artisan[0]}' assigned to team '{team[0]}' (Team ID: {team_id})")

    def get_projects(self):
        self.cursor.execute("SELECT * FROM projects")
        return self.cursor.fetchall()

    def get_artisans(self):
        self.cursor.execute("SELECT * FROM artisans")
        return self.cursor.fetchall()

    def get_assignments(self):
        self.cursor.execute("SELECT * FROM assignments")
        return self.cursor.fetchall()

    def log_activity(self, action, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO activity_log (action, details, timestamp)
            VALUES (?, ?, ?)
        ''', (action, details, timestamp))
        self.conn.commit()

    def get_recent_activities(self, limit=10):
        self.cursor.execute("SELECT action, details, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()