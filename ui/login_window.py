import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from db.database import Database

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gantt Artisan Program - Login")
        self.setFixedSize(300, 200)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        """Set up the login window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def handle_login(self):
        """Authenticate the user and handle login."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        try:
            user_info = self.db.login_user(username, password)
            QMessageBox.information(self, "Success", f"Welcome, {username}!\nRole: {user_info['role']}")
            self.open_main_window(user_info)
        except ValueError as e:
            QMessageBox.critical(self, "Login Failed", str(e))

    def open_main_window(self, user_info):
        """Open the main window after successful login."""
        from ui.main_window import MainWindow
        self.main_window = MainWindow(user_info)
        self.main_window.show()
        self.db.close()
        self.close()

    def closeEvent(self, event):
        """Ensure database connection is closed when window is closed."""
        self.db.close()
        event.accept()