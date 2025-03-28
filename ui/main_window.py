from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel)
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
        artisans_layout = QVBoxLayout(artisans_tab)
        artisans_layout.addWidget(QLabel("Artisans management placeholder"))
        tabs.addTab(artisans_tab, "Artisans")

        # Projects tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        projects_layout.addWidget(QLabel("Projects management placeholder"))
        tabs.addTab(projects_tab, "Projects")

        # Assignments tab
        assignments_tab = QWidget()
        assignments_layout = QVBoxLayout(assignments_tab)
        assignments_layout.addWidget(QLabel("Assignments management placeholder"))
        tabs.addTab(assignments_tab, "Assignments")

        # Audit Log tab (visible only to Construction Manager or Manager)
        if self.user_info['role'] in ["Construction Manager", "Manager"]:
            audit_tab = QWidget()
            audit_layout = QVBoxLayout(audit_tab)
            audit_layout.addWidget(QLabel("Audit log placeholder"))
            tabs.addTab(audit_tab, "Audit Log")

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        main_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignRight)

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
