# ui/login_window.py
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from db.database import Database

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gantt Artisan Program - Login")
        self.setGeometry(100, 100, 400, 500)
        self.db = Database(db_path="gantt.db")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logos/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(173, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("Guth")
            logo_label.setStyleSheet("color: #38a169; font-size: 18px; font-weight: bold; font-family: 'Roboto';")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel("Construction Manager")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Roboto'; color: #2d3748;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Login Form
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 8px; font-size: 14px; font-family: 'Roboto';")
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 14px; font-family: 'Roboto';")
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        # Login Button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("background-color: #38a169; color: white; padding: 10px; font-size: 14px; font-family: 'Roboto'; border-radius: 5px;")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        # Spacer
        layout.addStretch()

        # Footer
        footer_label = QLabel("Build 1.0.0 | Copyright Guth South Africa")
        footer_label.setStyleSheet("color: #2d3748; font-size: 10px; font-family: 'Roboto'; text-align: center; padding: 5px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        user = self.db.get_user(username, password)
        if user:
            self.close()
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password")