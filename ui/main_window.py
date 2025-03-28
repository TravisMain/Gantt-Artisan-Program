from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QMessageBox, QFormLayout)
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

        # Projects tab (unchanged placeholder)
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        projects_layout.addWidget(QLabel("Projects management placeholder"))
        tabs.addTab(projects_tab, "Projects")

        # Assignments tab (unchanged placeholder)
        assignments_tab = QWidget()
        assignments_layout = QVBoxLayout(assignments_tab)
        assignments_layout.addWidget(QLabel("Assignments management placeholder"))
        tabs.addTab(assignments_tab, "Assignments")

        # Audit Log tab (unchanged placeholder, role-restricted)
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

        # Table to display artisans
        self.artisans_table = QTableWidget()
        self.artisans_table.setColumnCount(7)
        self.artisans_table.setHorizontalHeaderLabels(["ID", "Name", "Team ID", "Skill", "Availability", "Hourly Rate", "Contact"])
        self.load_artisans_data()
        layout.addWidget(self.artisans_table)

        # Add artisan form (visible only to Construction Manager and Manager)
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

    def load_artisans_data(self):
        """Load artisans from the database into the table."""
        artisans = self.db.get_artisans()
        self.artisans_table.setRowCount(len(artisans))
        for row, artisan in enumerate(artisans):
            # artisan: (id, name, team_id, skill, availability, hourly_rate, contact_email, contact_phone)
            for col, value in enumerate(artisan):
                if col == 6:  # Combine email and phone into one "Contact" column
                    contact = f"{artisan[6] or ''} / {artisan[7] or ''}".strip(" / ")
                    item = QTableWidgetItem(contact)
                else:
                    item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make cells read-only
                self.artisans_table.setItem(row, col if col < 6 else 6, item)
        self.artisans_table.resizeColumnsToContents()

    def add_artisan(self):
        """Add a new artisan to the database."""
        name = self.name_input.text().strip()
        team_id = self.team_id_input.text().strip() or None
        skill = self.skill_input.text().strip()
        availability = self.availability_input.text().strip()
        hourly_rate = self.hourly_rate_input.text().strip() or None
        contact_email = self.contact_email_input.text().strip() or None
        contact_phone = self.contact_phone_input.text().strip() or None

        # Basic input validation
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
            self.load_artisans_data()  # Refresh table
            self.clear_add_form()
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