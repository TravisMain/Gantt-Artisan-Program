import sqlite3

class Database:
    def __init__(self, db_path="gantt.db"):
        """Initialize the SQLite database connection and create tables."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # Enable foreign key constraints
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables with constraints and indexes."""
        # Artisans table
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

        # Teams table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                manager_id INTEGER,
                FOREIGN KEY(manager_id) REFERENCES artisans(id) ON DELETE SET NULL
            );
        """)

        # Projects table
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

        # Assignments table
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

        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('Construction Manager', 'Manager', 'Viewer')),
                last_login TEXT
            );
        """)

        # Audit log table
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

        # Commit the changes to the database
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()

# Test the database creation
if __name__ == "__main__":
    db = Database()
    print("Database schema created successfully.")
    db.close()
