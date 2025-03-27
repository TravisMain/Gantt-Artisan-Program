import sqlite3

class Database:
    def __init__(self, db_path="gantt.db"):
        """Initialize the SQLite database connection and create tables."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables with constraints and indexes."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS artisans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team_id INTEGER,
                skill TEXT NOT NULL,
                availability TEXT CHECK(availability IN ('Full-time', 'Part-time', 'On-call')),
                hourly_rate REAL CHECK(hourly_rate >= 0),
                contact_email TEXT,
                contact_phone TEXT,
                FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE SET NULL,
                UNIQUE(name, skill, team_id)
            );
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_artisans_team ON artisans(team_id);")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                manager_id INTEGER,
                FOREIGN KEY(manager_id) REFERENCES artisans(id) ON DELETE SET NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT CHECK(status IN ('Active', 'Pending', 'Completed', 'Cancelled')),
                budget REAL CHECK(budget >= 0),
                CHECK(start_date <= end_date)
            );
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_dates ON projects(start_date, end_date);")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artisan_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                hours_per_day REAL CHECK(hours_per_day BETWEEN 1 AND 12),
                completed_hours REAL DEFAULT 0,
                notes TEXT,
                status TEXT CHECK(status IN ('Planned', 'In Progress', 'Completed', 'Cancelled')),
                priority INTEGER DEFAULT 0,
                FOREIGN KEY(artisan_id) REFERENCES artisans(id) ON DELETE CASCADE,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(artisan_id, project_id, start_date, end_date),
                CHECK(start_date <= end_date)
            );
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_artisan_dates ON assignments(artisan_id, start_date, end_date);")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('Construction Manager', 'Manager', 'Viewer')),
                last_login TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        self.conn.commit()

    # Artisan CRUD Methods
    def add_artisan(self, name, team_id, skill, availability, hourly_rate, contact_email, contact_phone):
        """Add a new artisan to the database."""
        try:
            self.cursor.execute("""
                INSERT INTO artisans (name, team_id, skill, availability, hourly_rate, contact_email, contact_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, team_id, skill, availability, hourly_rate, contact_email, contact_phone))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add artisan {name}: {e}")

    def get_artisans(self):
        """Retrieve all artisans."""
        return self.cursor.execute("SELECT * FROM artisans").fetchall()

    def update_artisan(self, artisan_id, name=None, team_id=None, skill=None, availability=None, hourly_rate=None, contact_email=None, contact_phone=None):
        """Update an existing artisan."""
        current = self.cursor.execute("SELECT * FROM artisans WHERE id = ?", (artisan_id,)).fetchone()
        if not current:
            raise ValueError(f"Artisan with ID {artisan_id} not found")
        updates = {
            "name": name if name is not None else current[1],
            "team_id": team_id if team_id is not None else current[2],
            "skill": skill if skill is not None else current[3],
            "availability": availability if availability is not None else current[4],
            "hourly_rate": hourly_rate if hourly_rate is not None else current[5],
            "contact_email": contact_email if contact_email is not None else current[6],
            "contact_phone": contact_phone if contact_phone is not None else current[7]
        }
        try:
            self.cursor.execute("""
                UPDATE artisans SET name = ?, team_id = ?, skill = ?, availability = ?, hourly_rate = ?, contact_email = ?, contact_phone = ?
                WHERE id = ?
            """, (updates["name"], updates["team_id"], updates["skill"], updates["availability"], updates["hourly_rate"],
                  updates["contact_email"], updates["contact_phone"], artisan_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to update artisan {artisan_id}: {e}")

    def delete_artisan(self, artisan_id):
        """Delete an artisan by ID."""
        self.cursor.execute("DELETE FROM artisans WHERE id = ?", (artisan_id,))
        if self.cursor.rowcount == 0:
            raise ValueError(f"Artisan with ID {artisan_id} not found")
        self.conn.commit()

    # Team CRUD Methods
    def add_team(self, name, description, manager_id):
        """Add a new team."""
        try:
            self.cursor.execute("INSERT INTO teams (name, description, manager_id) VALUES (?, ?, ?)", (name, description, manager_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add team {name}: {e}")

    def get_teams(self):
        """Retrieve all teams."""
        return self.cursor.execute("SELECT * FROM teams").fetchall()

    def update_team(self, team_id, name=None, description=None, manager_id=None):
        """Update an existing team."""
        current = self.cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
        if not current:
            raise ValueError(f"Team with ID {team_id} not found")
        updates = {
            "name": name if name is not None else current[1],
            "description": description if description is not None else current[2],
            "manager_id": manager_id if manager_id is not None else current[3]
        }
        try:
            self.cursor.execute("UPDATE teams SET name = ?, description = ?, manager_id = ? WHERE id = ?",
                               (updates["name"], updates["description"], updates["manager_id"], team_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to update team {team_id}: {e}")

    def delete_team(self, team_id):
        """Delete a team by ID."""
        self.cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        if self.cursor.rowcount == 0:
            raise ValueError(f"Team with ID {team_id} not found")
        self.conn.commit()

    # Project CRUD Methods
    def add_project(self, name, start_date, end_date, status, budget):
        """Add a new project."""
        try:
            self.cursor.execute("INSERT INTO projects (name, start_date, end_date, status, budget) VALUES (?, ?, ?, ?, ?)",
                               (name, start_date, end_date, status, budget))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add project {name}: {e}")

    def get_projects(self):
        """Retrieve all projects."""
        return self.cursor.execute("SELECT * FROM projects").fetchall()

    def update_project(self, project_id, name=None, start_date=None, end_date=None, status=None, budget=None):
        """Update an existing project."""
        current = self.cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not current:
            raise ValueError(f"Project with ID {project_id} not found")
        updates = {
            "name": name if name is not None else current[1],
            "start_date": start_date if start_date is not None else current[2],
            "end_date": end_date if end_date is not None else current[3],
            "status": status if status is not None else current[4],
            "budget": budget if budget is not None else current[5]
        }
        try:
            self.cursor.execute("UPDATE projects SET name = ?, start_date = ?, end_date = ?, status = ?, budget = ? WHERE id = ?",
                               (updates["name"], updates["start_date"], updates["end_date"], updates["status"], updates["budget"], project_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to update project {project_id}: {e}")

    def delete_project(self, project_id):
        """Delete a project by ID."""
        self.cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        if self.cursor.rowcount == 0:
            raise ValueError(f"Project with ID {project_id} not found")
        self.conn.commit()

    # Assignment CRUD Methods
    def add_assignment(self, artisan_id, project_id, start_date, end_date, hours_per_day, completed_hours=0, notes=None, status="Planned", priority=0):
        """Add a new assignment."""
        try:
            self.cursor.execute("""
                INSERT INTO assignments (artisan_id, project_id, start_date, end_date, hours_per_day, completed_hours, notes, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (artisan_id, project_id, start_date, end_date, hours_per_day, completed_hours, notes, status, priority))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add assignment: {e}")

    def get_assignments(self):
        """Retrieve all assignments."""
        return self.cursor.execute("SELECT * FROM assignments").fetchall()

    def update_assignment(self, assignment_id, artisan_id=None, project_id=None, start_date=None, end_date=None, hours_per_day=None,
                         completed_hours=None, notes=None, status=None, priority=None):
        """Update an existing assignment."""
        current = self.cursor.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
        if not current:
            raise ValueError(f"Assignment with ID {assignment_id} not found")
        updates = {
            "artisan_id": artisan_id if artisan_id is not None else current[1],
            "project_id": project_id if project_id is not None else current[2],
            "start_date": start_date if start_date is not None else current[3],
            "end_date": end_date if end_date is not None else current[4],
            "hours_per_day": hours_per_day if hours_per_day is not None else current[5],
            "completed_hours": completed_hours if completed_hours is not None else current[6],
            "notes": notes if notes is not None else current[7],
            "status": status if status is not None else current[8],
            "priority": priority if priority is not None else current[9]
        }
        try:
            self.cursor.execute("""
                UPDATE assignments SET artisan_id = ?, project_id = ?, start_date = ?, end_date = ?, hours_per_day = ?,
                completed_hours = ?, notes = ?, status = ?, priority = ? WHERE id = ?
            """, (updates["artisan_id"], updates["project_id"], updates["start_date"], updates["end_date"],
                  updates["hours_per_day"], updates["completed_hours"], updates["notes"], updates["status"],
                  updates["priority"], assignment_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to update assignment {assignment_id}: {e}")

    def delete_assignment(self, assignment_id):
        """Delete an assignment by ID."""
        self.cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        if self.cursor.rowcount == 0:
            raise ValueError(f"Assignment with ID {assignment_id} not found")
        self.conn.commit()

    # User CRUD Methods (basic, expanded later for authentication)
    def add_user(self, username, password_hash, role):
        """Add a new user."""
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to add user {username}: {e}")

    def get_users(self):
        """Retrieve all users."""
        return self.cursor.execute("SELECT * FROM users").fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()