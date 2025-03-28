# ui/login_window.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from db.database import Database

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gantt Artisan - Login")
        self.setFixedSize(300, 200)
        self.db = Database(db_path="gantt.db")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        user = self.db.get_user(username, password)
        if user and user["role"] == "Construction Manager":
            self.accept()
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials or role.")