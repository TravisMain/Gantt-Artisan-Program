from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QMessageBox, QFormLayout, 
                             QComboBox, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt
from db.database import Database

class EditArtisanDialog(QDialog):
    def __init__(self, artisan_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Artisan")
        self.artisan_data = artisan_data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.name_input = QLineEdit(self.artisan_data[1])
        self.team_id_input = QLineEdit(str(self.artisan_data[2]) if self.artisan_data[2] else "")
        self.skill_input = QLineEdit(self.artisan_data[3])
        self.availability_input = QLineEdit(self.artisan_data[4])
        self.hourly_rate_input = QLineEdit(str(self.artisan_data[5]) if self.artisan_data[5] else "")
        self.email_input = QLineEdit(self.artisan_data[6] or "")
        self.phone_input = QLineEdit(self.artisan_data[7] or "")

        layout.addRow("Name:", self.name_input)
        layout.addRow("Team ID:", self.team_id_input)
        layout.addRow("Skill:", self.skill_input)
        layout.addRow("Availability:", self.availability_input)
        layout.addRow("Hourly Rate:", self.hourly_rate_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Phone:", self.phone_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "team_id": self.team_id_input.text().strip() or None,
            "skill": self.skill_input.text().strip(),
            "availability": self.availability_input.text().strip(),
            "hourly_rate": self.hourly_rate_input.text().strip() or None,
            "contact_email": self.email_input.text().strip() or None,
            "contact_phone": self.phone_input.text().strip() or None
        }

class EditProjectDialog(QDialog):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project")
        self.project_data = project_data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.name_input = QLineEdit(self.project_data[1])
        self.start_date_input = QLineEdit(self.project_data[2])
        self.end_date_input = QLineEdit(self.project_data[3])
        self.status_input = QLineEdit(self.project_data[4])
        self.budget_input = QLineEdit(str(self.project_data[5]) if self.project_data[5] else "")

        layout.addRow("Name:", self.name_input)
        layout.addRow("Start Date:", self.start_date_input)
        layout.addRow("End Date:", self.end_date_input)
        layout.addRow("Status:", self.status_input)
        layout.addRow("Budget:", self.budget_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "start_date": self.start_date_input.text().strip(),
            "end_date": self.end_date_input.text().strip(),
            "status": self.status_input.text().strip(),
            "budget": self.budget_input.text().strip() or None
        }

class EditAssignmentDialog(QDialog):
    def __init__(self, assignment_data, artisans, projects, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Assignment")
        self.assignment_data = assignment_data
        self.artisans = artisans
        self.projects = projects
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.artisan_combo = QComboBox()
        for artisan in self.artisans:
            self.artisan_combo.addItem(f"{artisan[1]} (ID: {artisan[0]})", artisan[0])
        self.artisan_combo.setCurrentIndex([a[0] for a in self.artisans].index(self.assignment_data[1]))
        self.project_combo = QComboBox()
        for project in self.projects:
            self.project_combo.addItem(f"{project[1]} (ID: {project[0]})", project[0])
        self.project_combo.setCurrentIndex([p[0] for p in self.projects].index(self.assignment_data[2]))
        self.start_date_input = QLineEdit(self.assignment_data[3])
        self.end_date_input = QLineEdit(self.assignment_data[4])
        self.hours_per_day_input = QLineEdit(str(self.assignment_data[5]))

        layout.addRow("Artisan:", self.artisan_combo)
        layout.addRow("Project:", self.project_combo)
        layout.addRow("Start Date:", self.start_date_input)
        layout.addRow("End Date:", self.end_date_input)
        layout.addRow("Hours/Day:", self.hours_per_day_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "artisan_id": self.artisan_combo.currentData(),
            "project_id": self.project_combo.currentData(),
            "start_date": self.start_date_input.text().strip(),
            "end_date": self.end_date_input.text().strip(),
            "hours_per_day": self.hours_per_day_input.text().strip()
        }

class MainWindow(QMainWindow):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gantt Artisan Program - Main Dashboard")
        self.setMinimumSize(600, 400)
        self.user_info = user_info
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        welcome_label = QLabel(f"Welcome, User ID: {self.user_info['user_id']} | Role: {self.user_info['role']}")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        artisans_tab = QWidget()
        self.setup_artisans_tab(artisans_tab)
        tabs.addTab(artisans_tab, "Artisans")

        projects_tab = QWidget()
        self.setup_projects_tab(projects_tab)
        tabs.addTab(projects_tab, "Projects")

        assignments_tab = QWidget()
        self.setup_assignments_tab(assignments_tab)
        tabs.addTab(assignments_tab, "Assignments")

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            audit_tab = QWidget()
            self.setup_audit_log_tab(audit_tab)
            tabs.addTab(audit_tab, "Audit Log")

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        main_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignRight)

    def setup_artisans_tab(self, tab):
        layout = QVBoxLayout(tab)

        # Search and Filter
        search_layout = QHBoxLayout()
        self.artisan_search = QLineEdit()
        self.artisan_search.setPlaceholderText("Search by Name or Skill...")
        self.artisan_search.textChanged.connect(self.load_artisans_data)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.artisan_search)

        self.artisan_filter = QComboBox()
        self.artisan_filter.addItems(["All", "Full-time", "Part-time", "On-call"])
        self.artisan_filter.currentTextChanged.connect(self.load_artisans_data)
        search_layout.addWidget(QLabel("Filter Availability:"))
        search_layout.addWidget(self.artisan_filter)
        layout.addLayout(search_layout)

        # Table
        self.artisans_table = QTableWidget()
        self.artisans_table.setColumnCount(7)
        self.artisans_table.setHorizontalHeaderLabels(["ID", "Name", "Team ID", "Skill", "Availability", "Hourly Rate", "Contact"])
        self.load_artisans_data()
        layout.addWidget(self.artisans_table)

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            buttons_layout = QHBoxLayout()
            edit_button = QPushButton("Edit Selected")
            edit_button.clicked.connect(self.edit_artisan)
            delete_button = QPushButton("Delete Selected")
            delete_button.clicked.connect(self.delete_artisan)
            buttons_layout.addWidget(edit_button)
            buttons_layout.addWidget(delete_button)
            layout.addLayout(buttons_layout)

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
            layout.addWidget(QLabel("Viewing only - add/edit/delete restricted to managers."))

    def setup_projects_tab(self, tab):
        layout = QVBoxLayout(tab)

        # Search and Filter
        search_layout = QHBoxLayout()
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText("Search by Name...")
        self.project_search.textChanged.connect(self.load_projects_data)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.project_search)

        self.project_filter = QComboBox()
        self.project_filter.addItems(["All", "Active", "Pending", "Completed", "Cancelled"])
        self.project_filter.currentTextChanged.connect(self.load_projects_data)
        search_layout.addWidget(QLabel("Filter Status:"))
        search_layout.addWidget(self.project_filter)
        layout.addLayout(search_layout)

        # Table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels(["ID", "Name", "Start Date", "End Date", "Status"])
        self.load_projects_data()
        layout.addWidget(self.projects_table)

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            buttons_layout = QHBoxLayout()
            edit_button = QPushButton("Edit Selected")
            edit_button.clicked.connect(self.edit_project)
            delete_button = QPushButton("Delete Selected")
            delete_button.clicked.connect(self.delete_project)
            buttons_layout.addWidget(edit_button)
            buttons_layout.addWidget(delete_button)
            layout.addLayout(buttons_layout)

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
            layout.addWidget(QLabel("Viewing only - add/edit/delete restricted to managers."))

    def setup_assignments_tab(self, tab):
        layout = QVBoxLayout(tab)

        # Search and Filter
        search_layout = QHBoxLayout()
        self.assignment_search = QLineEdit()
        self.assignment_search.setPlaceholderText("Search by Artisan or Project...")
        self.assignment_search.textChanged.connect(self.load_assignments_data)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.assignment_search)

        self.assignment_filter = QComboBox()
        self.assignment_filter.addItems(["All", "Planned", "In Progress", "Completed", "Cancelled"])
        self.assignment_filter.currentTextChanged.connect(self.load_assignments_data)
        search_layout.addWidget(QLabel("Filter Status:"))
        search_layout.addWidget(self.assignment_filter)
        layout.addLayout(search_layout)

        # Table
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(6)
        self.assignments_table.setHorizontalHeaderLabels(["ID", "Artisan", "Project", "Start Date", "End Date", "Hours/Day"])
        self.load_assignments_data()
        layout.addWidget(self.assignments_table)

        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            buttons_layout = QHBoxLayout()
            edit_button = QPushButton("Edit Selected")
            edit_button.clicked.connect(self.edit_assignment)
            delete_button = QPushButton("Delete Selected")
            delete_button.clicked.connect(self.delete_assignment)
            buttons_layout.addWidget(edit_button)
            buttons_layout.addWidget(delete_button)
            layout.addLayout(buttons_layout)

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
            layout.addWidget(QLabel("Viewing only - add/edit/delete restricted to managers."))

    def setup_audit_log_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        self.audit_table.setHorizontalHeaderLabels(["ID", "User ID", "Action", "Timestamp", "Details"])
        self.load_audit_log_data()
        layout.addWidget(self.audit_table)

    def load_artisans_data(self):
        artisans = self.db.get_artisans()
        search_text = self.artisan_search.text().lower()
        filter_text = self.artisan_filter.currentText()

        filtered_artisans = []
        for artisan in artisans:
            if (search_text in artisan[1].lower() or search_text in artisan[3].lower()) and \
               (filter_text == "All" or artisan[4] == filter_text):
                filtered_artisans.append(artisan)

        self.artisans_table.setRowCount(len(filtered_artisans))
        for row, artisan in enumerate(filtered_artisans):
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
        projects = self.db.get_projects()
        search_text = self.project_search.text().lower()
        filter_text = self.project_filter.currentText()

        filtered_projects = []
        for project in projects:
            if search_text in project[1].lower() and \
               (filter_text == "All" or project[4] == filter_text):
                filtered_projects.append(project)

        self.projects_table.setRowCount(len(filtered_projects))
        for row, project in enumerate(filtered_projects):
            for col, value in enumerate(project[:-1]):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.projects_table.setItem(row, col, item)
        self.projects_table.resizeColumnsToContents()

    def load_assignments_data(self):
        assignments = self.db.get_assignments()
        search_text = self.assignment_search.text().lower()
        filter_text = self.assignment_filter.currentText()

        artisans = {a[0]: a[1] for a in self.db.get_artisans()}
        projects = {p[0]: p[1] for p in self.db.get_projects()}
        filtered_assignments = []
        for assignment in assignments:
            artisan_name = artisans.get(assignment[1], str(assignment[1])).lower()
            project_name = projects.get(assignment[2], str(assignment[2])).lower()
            if (search_text in artisan_name or search_text in project_name) and \
               (filter_text == "All" or assignment[8] == filter_text):
                filtered_assignments.append(assignment)

        self.assignments_table.setRowCount(len(filtered_assignments))
        for row, assignment in enumerate(filtered_assignments):
            values = [
                str(assignment[0]),
                artisans.get(assignment[1], str(assignment[1])),
                projects.get(assignment[2], str(assignment[2])),
                assignment[3],
                assignment[4],
                str(assignment[5])
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assignments_table.setItem(row, col, item)
        self.assignments_table.resizeColumnsToContents()

    def load_audit_log_data(self):
        audit_logs = self.db.get_audit_logs()
        self.audit_table.setRowCount(len(audit_logs))
        for row, log in enumerate(audit_logs):
            for col, value in enumerate(log):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.audit_table.setItem(row, col, item)
        self.audit_table.resizeColumnsToContents()

    def load_artisans_into_combo(self):
        self.artisan_combo.clear()
        artisans = self.db.get_artisans()
        for artisan in artisans:
            self.artisan_combo.addItem(f"{artisan[1]} (ID: {artisan[0]})", artisan[0])

    def load_projects_into_combo(self):
        self.project_combo.clear()
        projects = self.db.get_projects()
        for project in projects:
            self.project_combo.addItem(f"{project[1]} (ID: {project[0]})", project[0])

    def add_artisan(self):
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

    def edit_artisan(self):
        selected = self.artisans_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an artisan to edit.")
            return
        artisan_id = int(self.artisans_table.item(selected, 0).text())
        artisan_data = self.db.get_artisan_by_id(artisan_id)
        dialog = EditArtisanDialog(artisan_data, self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["name"] or not data["skill"] or not data["availability"]:
                QMessageBox.warning(self, "Input Error", "Name, Skill, and Availability are required.")
                return
            if data["availability"] not in ["Full-time", "Part-time", "On-call"]:
                QMessageBox.warning(self, "Input Error", "Availability must be Full-time, Part-time, or On-call.")
                return
            try:
                if data["hourly_rate"]:
                    data["hourly_rate"] = float(data["hourly_rate"])
                    if data["hourly_rate"] < 0:
                        raise ValueError
                if data["team_id"]:
                    data["team_id"] = int(data["team_id"])
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Team ID must be an integer, Hourly Rate must be a non-negative number.")
                return
            try:
                self.db.update_artisan(self.user_info['user_id'], artisan_id, **data)
                QMessageBox.information(self, "Success", f"Artisan {data['name']} updated.")
                self.load_artisans_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_artisan(self):
        selected = self.artisans_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an artisan to delete.")
            return
        artisan_id = int(self.artisans_table.item(selected, 0).text())
        name = self.artisans_table.item(selected, 1).text()
        assignments = self.db.cursor.execute("SELECT id FROM assignments WHERE artisan_id = ?", (artisan_id,)).fetchall()
        msg = f"Are you sure you want to delete {name}?"
        if assignments:
            msg += f"\nThis will also delete {len(assignments)} associated assignment(s): {', '.join(str(a[0]) for a in assignments)}."
        if QMessageBox.question(self, "Confirm Delete", msg,
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_artisan(self.user_info['user_id'], artisan_id)
                QMessageBox.information(self, "Success", f"Artisan {name} and associated assignments deleted.")
                self.load_artisans_data()
                self.load_assignments_data()  # Refresh assignments tab
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def add_project(self):
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

    def edit_project(self):
        selected = self.projects_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a project to edit.")
            return
        project_id = int(self.projects_table.item(selected, 0).text())
        project_data = self.db.get_project_by_id(project_id)
        dialog = EditProjectDialog(project_data, self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["name"] or not data["start_date"] or not data["end_date"] or not data["status"]:
                QMessageBox.warning(self, "Input Error", "Name, Start Date, End Date, and Status are required.")
                return
            if data["status"] not in ["Active", "Pending", "Completed", "Cancelled"]:
                QMessageBox.warning(self, "Input Error", "Status must be Active, Pending, Completed, or Cancelled.")
                return
            if not (self.db.validate_date(data["start_date"]) and self.db.validate_date(data["end_date"])):
                QMessageBox.warning(self, "Input Error", "Dates must be in YYYY-MM-DD format.")
                return
            if not self.db.check_date_order(data["start_date"], data["end_date"]):
                QMessageBox.warning(self, "Input Error", "Start Date must be before or equal to End Date.")
                return
            try:
                if data["budget"]:
                    data["budget"] = float(data["budget"])
                    if data["budget"] < 0:
                        raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Budget must be a non-negative number.")
                return
            try:
                self.db.update_project(self.user_info['user_id'], project_id, **data)
                QMessageBox.information(self, "Success", f"Project {data['name']} updated.")
                self.load_projects_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_project(self):
        selected = self.projects_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a project to delete.")
            return
        project_id = int(self.projects_table.item(selected, 0).text())
        name = self.projects_table.item(selected, 1).text()
        assignments = self.db.cursor.execute("SELECT id FROM assignments WHERE project_id = ?", (project_id,)).fetchall()
        msg = f"Are you sure you want to delete {name}?"
        if assignments:
            msg += f"\nThis will also delete {len(assignments)} associated assignment(s): {', '.join(str(a[0]) for a in assignments)}."
        if QMessageBox.question(self, "Confirm Delete", msg,
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_project(self.user_info['user_id'], project_id)
                QMessageBox.information(self, "Success", f"Project {name} and associated assignments deleted.")
                self.load_projects_data()
                self.load_assignments_data()  # Refresh assignments tab
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def add_assignment(self):
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

    def edit_assignment(self):
        selected = self.assignments_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an assignment to edit.")
            return
        assignment_id = int(self.assignments_table.item(selected, 0).text())
        assignment_data = self.db.get_assignment_by_id(assignment_id)
        dialog = EditAssignmentDialog(assignment_data, self.db.get_artisans(), self.db.get_projects(), self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["start_date"] or not data["end_date"] or not data["hours_per_day"]:
                QMessageBox.warning(self, "Input Error", "Start Date, End Date, and Hours/Day are required.")
                return
            if not (self.db.validate_date(data["start_date"]) and self.db.validate_date(data["end_date"])):
                QMessageBox.warning(self, "Input Error", "Dates must be in YYYY-MM-DD format.")
                return
            if not self.db.check_date_order(data["start_date"], data["end_date"]):
                QMessageBox.warning(self, "Input Error", "Start Date must be before or equal to End Date.")
                return
            try:
                data["hours_per_day"] = float(data["hours_per_day"])
                if not 1 <= data["hours_per_day"] <= 12:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Hours/Day must be a number between 1 and 12.")
                return
            try:
                self.db.update_assignment(self.user_info['user_id'], assignment_id, **data)
                QMessageBox.information(self, "Success", "Assignment updated.")
                self.load_assignments_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_assignment(self):
        selected = self.assignments_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select an assignment to delete.")
            return
        assignment_id = int(self.assignments_table.item(selected, 0).text())
        if QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete assignment ID {assignment_id}?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_assignment(self.user_info['user_id'], assignment_id)
                QMessageBox.information(self, "Success", f"Assignment {assignment_id} deleted.")
                self.load_assignments_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def clear_add_form(self):
        self.name_input.clear()
        self.team_id_input.clear()
        self.skill_input.clear()
        self.availability_input.clear()
        self.hourly_rate_input.clear()
        self.contact_email_input.clear()
        self.contact_phone_input.clear()

    def clear_project_form(self):
        self.project_name_input.clear()
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.status_input.clear()
        self.budget_input.clear()

    def clear_assignment_form(self):
        self.assign_start_date_input.clear()
        self.assign_end_date_input.clear()
        self.hours_per_day_input.clear()

    def logout(self):
        self.db.close()
        self.close()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def closeEvent(self, event):
        self.db.close()
        event.accept()