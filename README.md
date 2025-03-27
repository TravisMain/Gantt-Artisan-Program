Final Development Plan for the Gantt Artisan Program

This document provides a detailed, step-by-step guide for developing the Gantt Artisan Program, a standalone desktop application for managing artisan schedules, project assignments, and timesheets for Guth South Africa PTY LTD. The plan is divided into five phases, each with specific objectives, tasks, and instructions. It includes code snippets, rationales, and additional considerations to ensure the program is robust, scalable, and user-friendly.
Phase 1: Planning and Setup

Objective: Establish a solid foundation for the program, including the database schema, project structure, and initial data.
1.1 Define Database Schema

    Database: SQLite (gantt.db)
    Tables:
        artisans:
        sql

CREATE TABLE artisans (
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
CREATE INDEX idx_artisans_team ON artisans(team_id);
teams:
sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    manager_id INTEGER,
    FOREIGN KEY(manager_id) REFERENCES artisans(id) ON DELETE SET NULL
);
projects:
sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT CHECK(status IN ('Active', 'Pending', 'Completed', 'Cancelled')),
    budget REAL CHECK(budget >= 0),
    CHECK(start_date <= end_date)
);
CREATE INDEX idx_projects_dates ON projects(start_date, end_date);
assignments:
sql
CREATE TABLE assignments (
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
CREATE INDEX idx_assignments_artisan_dates ON assignments(artisan_id, start_date, end_date);
users:
sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('Construction Manager', 'Manager', 'Viewer')),
    last_login TEXT
);
audit_log:
sql

        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    Rationale: The schema ensures data integrity with constraints (e.g., UNIQUE, CHECK) and optimizes queries with indexes. New fields like priority in assignments and audit_log for tracking changes enhance functionality and accountability.

1.2 Set Up Project Structure

    Directory Structure:
    text

gantt_artisan/
├── db/
│   ├── __init__.py
│   └── database.py
├── ui/
│   ├── __init__.py
│   ├── main.py
│   ├── login.py
│   ├── gantt.py
│   ├── sidebar.py
│   ├── quick_update.py
│   ├── export.py
│   ├── settings.py
│   └── logs.py
├── tests/
│   ├── __init__.py
│   └── test_database.py
├── docs/
│   └── README.md
├── resources/
│   ├── icons/
│   └── stylesheets/
├── config.py
└── requirements.txt
Configuration File (config.py):
python

    DATABASE_PATH = "gantt.db"
    AUTOSAVE_INTERVAL = 300000  # 5 minutes in milliseconds
    DEFAULT_HOURS_CAP = 12
    THEME = "light"  # Options: "light" or "dark"
    SESSION_TIMEOUT = 1800  # 30 minutes in seconds
    BACKUP_INTERVAL = 86400000  # 24 hours in milliseconds
    Rationale: A modular structure improves maintainability, while config.py centralizes settings like session timeouts and backup intervals.

1.3 Seed Initial Data

    Objective: Populate the database with test data to simulate real-world scenarios.
    Instructions:
        Create seed_db.py to insert 100 artisans, 100 projects, and varied assignments (e.g., overlapping dates, completed tasks, cancelled tasks).
        Include edge cases to test validation and UI rendering.
    Rationale: Diverse data ensures thorough testing of features like overlap detection and UI scalability.

1.4 Initialize Version Control

    Instructions:
        Initialize a Git repository:
        bash

        git init
        echo "gantt.db" > .gitignore
        git add .
        git commit -m "Initial project setup with schema and structure"
    Rationale: Version control tracks changes and supports collaboration.

Phase 2: Core Backend Development

Objective: Build a secure and reliable backend with data access, validation, authentication, and logging.
2.1 Implement Data Access Layer

    ORM: Use SQLAlchemy for database operations.
    Example for adding an artisan:
    python

from sqlalchemy.orm import Session
from db.models import Artisan

def add_artisan(session: Session, name, team_id, skill, availability, hourly_rate, email, phone):
    artisan = Artisan(name=name, team_id=team_id, skill=skill, availability=availability,
                      hourly_rate=hourly_rate, contact_email=email, contact_phone=phone)
    session.add(artisan)
    session.commit()
    return artisan.id
Error Handling:

    Catch exceptions for duplicate entries or invalid data:
    python

        except IntegrityError as e:
            session.rollback()
            raise ValueError("Artisan already exists or invalid data")
    Rationale: SQLAlchemy simplifies database interactions, while error handling ensures robustness.

2.2 Add Validation Logic

    Assignment Validation:
        Check for date overlaps, hours constraints, and artisan availability.
        Use transactions for batch operations:
        python

        def assign_batch(session: Session, assignments):
            try:
                session.bulk_save_objects(assignments)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
    Rationale: Validation prevents scheduling conflicts, and transactions ensure data consistency during batch operations.

2.3 Enhance Authentication

    Password Policy: Enforce 8+ characters with at least one number.
    Session Timeouts: Implement via config.py.
    Password Hashing:
    python

    import bcrypt

    def hash_password(password):
        if len(password) < 8 or not any(c.isdigit() for c in password):
            raise ValueError("Password must be 8+ characters with at least one number")
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    Rationale: Strong authentication protects user data and ensures only authorized access.

2.4 Add Logging

    Audit Log:
        Log changes to the audit_log table for accountability:
        python

        def log_action(session, user_id, action, details):
            log_entry = AuditLog(user_id=user_id, action=action, details=details)
            session.add(log_entry)
            session.commit()
    Rationale: Logging provides a trail for debugging and auditing user actions.

Phase 3: Frontend Development – Basic Build

Objective: Create an intuitive and interactive user interface.
3.1 Create Login Screen

    Features:
        Username/password fields.
        "Forgot Password" link (placeholder for future implementation).
        Enforce password policy on user creation.
    Rationale: A secure login ensures only authorized users access the system.

3.2 Initialize Main Window

    Components:
        QMainWindow with menu bar, status bar, and central widget.
        Support for light/dark themes via Qt stylesheets in resources/.
        Keyboard shortcuts (e.g., Ctrl+S for save).
    Rationale: A polished UI with theme support and shortcuts improves usability.

3.3 Build Interactive Gantt Chart

    Implementation:
        Use QGraphicsView for rendering timelines and assignments.
        Add a zoom slider for adjustable views (day, week, month).
        Enable drag-and-drop to reschedule tasks with real-time validation.
    Rationale: Interactivity and scalability make the Gantt chart user-friendly and efficient.

3.4 Develop Sidebar

    Features:
        Searchable list of artisans, teams, and projects.
        "Favorites" section for quick access.
        Context menus for quick edits (e.g., change status, adjust hours).
    Rationale: Streamlined navigation and management enhance productivity.

Phase 4: Advanced Features

Objective: Enhance the program with advanced functionality for usability and efficiency.
4.1 Implement Quick Update Form

    Features:
        Pop-up form for editing assignments with real-time validation.
        Undo/redo support via a command pattern:
        python

        class Command:
            def execute(self): pass
            def undo(self): pass

        class UpdateAssignmentCommand(Command):
            def __init__(self, assignment, new_data):
                self.assignment = assignment
                self.old_data = assignment.__dict__.copy()
                self.new_data = new_data

            def execute(self):
                self.assignment.update(self.new_data)

            def undo(self):
                self.assignment.update(self.old_data)
    Rationale: Undo/redo and validation improve user experience and data accuracy.

4.2 Enhance Drill-Down

    Features:
        Click on a Gantt bar to view/edit details.
        Tooltips for quick information without opening full details.
        Visual cues (e.g., colors) for status and conflicts.
    Rationale: Quick access to information and visual indicators streamline workflows.

4.3 Add Flexible Export Functionality

    Features:
        Export filtered data to CSV or PDF with a progress bar for large datasets.
        Example for CSV export:
        python

        import csv
        from PyQt5.QtWidgets import QProgressDialog

        def export_assignments(session, filename, filters):
            progress = QProgressDialog("Exporting...", "Cancel", 0, 100)
            progress.show()
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Artisan", "Project", "Start", "End", "Hours"])
                assignments = session.query(Assignment).filter_by(**filters).all()
                for i, assignment in enumerate(assignments):
                    progress.setValue((i + 1) * 100 // len(assignments))
                    writer.writerow([assignment.artisan.name, assignment.project.name,
                                    assignment.start_date, assignment.end_date, assignment.hours_per_day])
    Rationale: Flexible exports meet diverse reporting needs, while progress tracking improves user experience.

Phase 5: Finalization and Optional Future Integration

Objective: Polish the application, add analytics, and prepare for deployment.
5.1 Implement Efficient Autosave

    Implementation:
        Use a QTimer to save every AUTOSAVE_INTERVAL milliseconds after changes.
        Show "Saved" in the status bar.
    Rationale: Autosave protects data without disrupting the user.

5.2 Add Analytics Dashboard

    Features:
        Use QChartView to display metrics like artisan utilization and project progress.
        Example:
        python

        from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet

        def create_utilization_chart(session):
            chart = QChart()
            series = QBarSeries()
            artisans = session.query(Artisan).all()
            for artisan in artisans:
                set = QBarSet(artisan.name)
                utilization = calculate_utilization(artisan)
                set.append(utilization)
                series.append(set)
            chart.addSeries(series)
            chart_view = QChartView(chart)
            return chart_view
    Rationale: Analytics provide actionable insights for managers.

5.3 Package the Application

    Instructions:
        Use PyInstaller: pyinstaller --onefile main.py
        Create an installer with Inno Setup, bundling the executable, database, and resources/.
    Rationale: A standalone installer simplifies deployment.

5.4 Plan for SAGE 300 Integration

    Instructions:
        Design a CSV export format matching SAGE 300 requirements.
        Document integration steps for future developers.
    Rationale: Prepares the program for seamless ERP integration.

5.5 Conduct Comprehensive Testing

    Instructions:
        Run unit tests for backend logic, integration tests for UI-database interactions, and load tests with 200+ artisans/projects.
        Optimize performance using profiling tools like cProfile.
    Rationale: Ensures reliability and scalability under real-world conditions.

Additional Development Considerations
Security

    Session Timeouts: Automatically log out inactive users after SESSION_TIMEOUT seconds.
    Dependency Updates: Regularly update dependencies using pip list --outdated.

User Feedback

    "Report Issue" Button: Link to an email or form for user feedback.
    User Acceptance Testing (UAT): Conduct with stakeholders to validate requirements.

Documentation

    User Manual: Create a PDF/HTML guide with screenshots and instructions.
    Code Comments: Include inline comments for maintainability.

Deployment and Updates

    Auto-Update Feature: Check for new versions from a server.
    Release Notes: Document changes with each update.

New Features

    Backup System: Export the database to a backup file periodically.
    Multi-Language Support: Use Qt’s tr() function for translations.
    Analytics Dashboard: Provide insights into artisan utilization and project progress.
