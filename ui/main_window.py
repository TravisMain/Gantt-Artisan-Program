from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QMessageBox, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt
from db.database import Database

class MainWindow(QMainWindow):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gantt Artisan Program - Main Dashboard")
        self.setMinimumSize(600, 400)
        self.user_info = user_info  # Store user_id and role from login
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        """Set up the main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Welcome message
        welcome_label = QLabel(f"Welcome, User ID: {self.user_info['user_id']} | Role: {self.user_info['role']}")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)

        # Tabbed interface
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Artisans tab
        artisans_tab = QWidget()
        self.setup_artisans_tab(artisans_tab)
        tabs.addTab(artisans_tab, "Artisans")

        # Projects tab
        projects_tab = QWidget()
        self.setup_projects_tab(projects_tab)
        tabs.addTab(projects_tab, "Projects")

        # Assignments tab
        assignments_tab = QWidget()
        self.setup_assignments_tab(assignments_tab)
        tabs.addTab(assignments_tab, "Assignments")

        # Audit Log tab (role-restricted)
        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            audit_tab = QWidget()
            audit_layout = QVBoxLayout(audit_tab)
            audit_layout.addWidget(QLabel("Audit log placeholder"))
            tabs.addTab(audit_tab, "Audit Log")

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        main_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignRight)

    def setup_artisans_tab(self, tab):
        """Set up the Artisans tab with a table and add form."""
        layout = QVBoxLayout(tab)
        self.artisans_table = QTableWidget()
        self.artisans_table.setColumnCount(7)
        self.artisans_table.setHorizontalHeaderLabels(["ID", "Name", "Team ID", "Skill", "Availability", "Hourly Rate", "Contact"])
        self.load_artisans_data()
        layout.addWidget(self.artisans_table)

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            add_form_widget = QWidget()
            add_form_layout = QFormLayout(add_form_widget)
            self.name_input = QLineEdit()
            self.team_id_input = QLineEdit()
            self.skill_input = QLineEdit()
            self.availability_input = QLineEdit()
            self.hourly_rate_input = QLineEdit()
            self.contact_email_input = QLineEdit()
            self.contact_phone_input = QLineEdit()

            add_form_layout.addRow("Name:", self.name_input)
            add_form_layout.addRow("Team ID:", self.team_id_input)
            add_form_layout.addRow("Skill:", self.skill_input)
            add_form_layout.addRow("Availability:", self.availability_input)
            add_form_layout.addRow("Hourly Rate:", self.hourly_rate_input)
            add_form_layout.addRow("Email:", self.contact_email_input)
            add_form_layout.addRow("Phone:", self.contact_phone_input)

            add_button = QPushButton("Add Artisan")
            add_button.clicked.connect(self.add_artisan)
            add_form_layout.addRow(add_button)
            layout.addWidget(add_form_widget)
        else:
            layout.addWidget(QLabel("Viewing only - add functionality restricted to managers."))

    def setup_projects_tab(self, tab):
        """Set up the Projects tab with a table and add form."""
        layout = QVBoxLayout(tab)
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels(["ID", "Name", "Start Date", "End Date", "Status"])
        self.load_projects_data()
        layout.addWidget(self.projects_table)

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            add_form_widget = QWidget()
            add_form_layout = QFormLayout(add_form_widget)
            self.project_name_input = QLineEdit()
            self.start_date_input = QLineEdit()
            self.start_date_input.setPlaceholderText("YYYY-MM-DD")
            self.end_date_input = QLineEdit()
            self.end_date_input.setPlaceholderText("YYYY-MM-DD")
            self.status_input = QLineEdit()
            self.budget_input = QLineEdit()

            add_form_layout.addRow("Name:", self.project_name_input)
            add_form_layout.addRow("Start Date:", self.start_date_input)
            add_form_layout.addRow("End Date:", self.end_date_input)
            add_form_layout.addRow("Status:", self.status_input)
            add_form_layout.addRow("Budget:", self.budget_input)

            add_button = QPushButton("Add Project")
            add_button.clicked.connect(self.add_project)
            add_form_layout.addRow(add_button)
            layout.addWidget(add_form_widget)
        else:
            layout.addWidget(QLabel("Viewing only - add functionality restricted to managers."))

    def setup_assignments_tab(self, tab):
        """Set up the Assignments tab with a table and add form."""
        layout = QVBoxLayout(tab)

        # Table to display assignments
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(6)
        self.assignments_table.setHorizontalHeaderLabels(["ID", "Artisan", "Project", "Start Date", "End Date", "Hours/Day"])
        self.load_assignments_data()
        layout.addWidget(self.assignments_table)

        # Add assignment form (visible only to Construction Manager and Manager)
        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            add_form_widget = QWidget()
            add_form_layout = QFormLayout(add_form_widget)

            self.artisan_combo = QComboBox()
            self.load_artisans_into_combo()
            self.project_combo = QComboBox()
            self.load_projects_into_combo()
            self.assign_start_date_input = QLineEdit()
            self.assign_start_date_input.setPlaceholderText("YYYY-MM-DD")
            self.assign_end_date_input = QLineEdit()
            self.assign_end_date_input.setPlaceholderText("YYYY-MM-DD")
            self.hours_per_day_input = QLineEdit()

            add_form_layout.addRow("Artisan:", self.artisan_combo)
            add_form_layout.addRow("Project:", self.project_combo)
            add_form_layout.addRow("Start Date:", self.assign_start_date_input)
            add_form_layout.addRow("End Date:", self.assign_end_date_input)
            add_form_layout.addRow("Hours/Day:", self.hours_per_day_input)

            add_button = QPushButton("Add Assignment")
            add_button.clicked.connect(self.add_assignment)
            add_form_layout.addRow(add_button)

            layout.addWidget(add_form_widget)
        else:
            layout.addWidget(QLabel("Viewing only - add functionality restricted to managers."))

    def load_artisans_data(self):
        """Load artisans from the database into the table."""
        artisans = self.db.get_artisans()
        self.artisans_table.setRowCount(len(artisans))
        for row, artisan in enumerate(artisans):
            for col, value in enumerate(artisan):
                if col == 6:
                    contact = f"{artisan[6] or ''} / {artisan[7] or ''}".strip(" / ")
                    item = QTableWidgetItem(contact)
                else:
                    item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.artisans_table.setItem(row, col if col < 6 else 6, item)
        self.artisans_table.resizeColumnsToContents()

    def load_projects_data(self):
        """Load projects from the database into the table."""
        projects = self.db.get_projects()
        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            for col, value in enumerate(project[:-1]):  # Exclude budget
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.projects_table.setItem(row, col, item)
        self.projects_table.resizeColumnsToContents()

    def load_assignments_data(self):
        """Load assignments from the database into the table."""
        assignments = self.db.get_assignments()
        self.assignments_table.setRowCount(len(assignments))
        artisans = {a[0]: a[1] for a in self.db.get_artisans()}  # Map ID to name
        projects = {p[0]: p[1] for p in self.db.get_projects()}  # Map ID to name
        for row, assignment in enumerate(assignments):
            # assignment: (id, artisan_id, project_id, start_date, end_date, hours_per_day, ...)
            values = [
                str(assignment[0]),  # ID
                artisans.get(assignment[1], str(assignment[1])),  # Artisan name or ID
                projects.get(assignment[2], str(assignment[2])),  # Project name or ID
                assignment[3],  # Start Date
                assignment[4],  # End Date
                str(assignment[5])  # Hours/Day
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assignments_table.setItem(row, col, item)
        self.assignments_table.resizeColumnsToContents()

    def load_artisans_into_combo(self):
        """Populate the artisan dropdown with names and IDs."""
        self.artisan_combo.clear()
        artisans = self.db.get_artisans()
        for artisan in artisans:
            self.artisan_combo.addItem(f"{artisan[1]} (ID: {artisan[0]})", artisan[0])

    def load_projects_into_combo(self):
        """Populate the project dropdown with names and IDs."""
        self.project_combo.clear()
        projects = self.db.get_projects()
        for project in projects:
            self.project_combo.addItem(f"{project[1]} (ID: {project[0]})", project[0])

    def add_artisan(self):
        """Add a new artisan to the database."""
        name = self.name_input.text().strip()
        team_id = self.team_id_input.text().strip() or None
        skill = self.skill_input.text().strip()
        availability = self.availability_input.text().strip()
        hourly_rate = self.hourly_rate_input.text().strip() or None
        contact_email = self.contact_email_input.text().strip() or None
        contact_phone = self.contact_phone_input.text().strip() or None

        if not name or not skill or not availability:
            QMessageBox.warning(self, "Input Error", "Name, Skill, and Availability are required.")
            return
        if availability not in ["Full-time", "Part-time", "On-call"]:
            QMessageBox.warning(self, "Input Error", "Availability must be Full-time, Part-time, or On-call.")
            return
        try:
            if hourly_rate:
                hourly_rate = float(hourly_rate)
                if hourly_rate < 0:
                    raise ValueError
            if team_id:
                team_id = int(team_id)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Team ID must be an integer, Hourly Rate must be a non-negative number.")
            return

        try:
            artisan_id = self.db.add_artisan(self.user_info['user_id'], name, team_id, skill, availability, 
                                            hourly_rate, contact_email, contact_phone)
            QMessageBox.information(self, "Success", f"Artisan {name} added with ID {artisan_id}.")
            self.load_artisans_data()
            self.clear_add_form()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_project(self):
        """Add a new project to the database."""
        name = self.project_name_input.text().strip()
        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()
        status = self.status_input.text().strip()
        budget = self.budget_input.text().strip() or None

        if not name or not start_date or not end_date or not status:
            QMessageBox.warning(self, "Input Error", "Name, Start Date, End Date, and Status are required.")
            return
        if status not in ["Active", "Pending", "Completed", "Cancelled"]:
            QMessageBox.warning(self, "Input Error", "Status must be Active, Pending, Completed, or Cancelled.")
            return
        if not (self.db.validate_date(start_date) and self.db.validate_date(end_date)):
            QMessageBox.warning(self, "Input Error", "Dates must be in YYYY-MM-DD format.")
            return
        if not self.db.check_date_order(start_date, end_date):
            QMessageBox.warning(self, "Input Error", "Start Date must be before or equal to End Date.")
            return
        try:
            if budget:
                budget = float(budget)
                if budget < 0:
                    raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Budget must be a non-negative number.")
            return

        try:
            project_id = self.db.add_project(self.user_info['user_id'], name, start_date, end_date, status, budget)
            QMessageBox.information(self, "Success", f"Project {name} added with ID {project_id}.")
            self.load_projects_data()
            self.clear_project_form()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_assignment(self):
        """Add a new assignment to the database."""
        artisan_id = self.artisan_combo.currentData()
        project_id = self.project_combo.currentData()
        start_date = self.assign_start_date_input.text().strip()
        end_date = self.assign_end_date_input.text().strip()
        hours_per_day = self.hours_per_day_input.text().strip()

        if not start_date or not end_date or not hours_per_day:
            QMessageBox.warning(self, "Input Error", "Start Date, End Date, and Hours/Day are required.")
            return
        if not (self.db.validate_date(start_date) and self.db.validate_date(end_date)):
            QMessageBox.warning(self, "Input Error", "Dates must be in YYYY-MM-DD format.")
            return
        if not self.db.check_date_order(start_date, end_date):
            QMessageBox.warning(self, "Input Error", "Start Date must be before or equal to End Date.")
            return
        try:
            hours_per_day = float(hours_per_day)
            if not 1 <= hours_per_day <= 12:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Hours/Day must be a number between 1 and 12.")
            return

        try:
            assignment_id = self.db.add_assignment(self.user_info['user_id'], artisan_id, project_id, 
                                                 start_date, end_date, hours_per_day)
            QMessageBox.information(self, "Success", f"Assignment added with ID {assignment_id}.")
            self.load_assignments_data()
            self.clear_assignment_form()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def clear_add_form(self):
        """Clear the add artisan form fields."""
        self.name_input.clear()
        self.team_id_input.clear()
        self.skill_input.clear()
        self.availability_input.clear()
        self.hourly_rate_input.clear()
        self.contact_email_input.clear()
        self.contact_phone_input.clear()

    def clear_project_form(self):
        """Clear the add project form fields."""
        self.project_name_input.clear()
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.status_input.clear()
        self.budget_input.clear()

    def clear_assignment_form(self):
        """Clear the add assignment form fields."""
        self.assign_start_date_input.clear()
        self.assign_end_date_input.clear()
        self.hours_per_day_input.clear()

    def logout(self):
        """Close the main window and return to login."""
        self.db.close()
        self.close()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def closeEvent(self, event):
        """Ensure database connection is closed when window is closed."""
        self.db.close()
        event.accept()