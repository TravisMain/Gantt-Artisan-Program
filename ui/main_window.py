# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QFormLayout, QDialog, QDialogButtonBox, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from db.database import Database
from ui.styles.stylesheet import STYLESHEET
from ui.tabs.dashboard import DashboardTab
from ui.tabs.calendar import CalendarTab
from ui.tabs.projects import ProjectsTab
from ui.tabs.artisans import ArtisansTab
from ui.tabs.reports import ReportsTab
from ui.tabs.timesheets import TimesheetsTab
from ui.tabs.documents import DocumentsTab
from ui.tabs.goals import GoalsTab
from ui.tabs.feedback import FeedbackTab
from datetime import datetime, timedelta

class AddItemDialog(QDialog):
    def __init__(self, item_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add {item_type}")
        self.item_type = item_type
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        if self.item_type == "Artisan":
            self.name_input = QLineEdit()
            self.skill_input = QLineEdit()
            self.availability_input = QLineEdit()
            layout.addRow("Name:", self.name_input)
            layout.addRow("Skill:", self.skill_input)
            layout.addRow("Availability:", self.availability_input)
        elif self.item_type == "Project":
            self.name_input = QLineEdit()
            self.start_date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
            self.end_date_input = QLineEdit((datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))
            self.status_input = QLineEdit("Active")
            self.job_number_input = QLineEdit()
            self.description_input = QLineEdit()
            layout.addRow("Name:", self.name_input)
            layout.addRow("Start Date:", self.start_date_input)
            layout.addRow("End Date:", self.end_date_input)
            layout.addRow("Status:", self.status_input)
            layout.addRow("Job Number:", self.job_number_input)
            layout.addRow("Description:", self.description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        if self.item_type == "Artisan":
            return {
                "name": self.name_input.text().strip(),
                "skill": self.skill_input.text().strip(),
                "availability": self.availability_input.text().strip()
            }
        elif self.item_type == "Project":
            return {
                "name": self.name_input.text().strip(),
                "start_date": self.start_date_input.text().strip(),
                "end_date": self.end_date_input.text().strip(),
                "status": self.status_input.text().strip(),
                "job_number": self.job_number_input.text().strip(),
                "description": self.description_input.text().strip()
            }

class MainWindow(QMainWindow):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gantt Artisan Program")
        self.setMinimumSize(1200, 800)
        self.user_info = user_info
        self.db = Database(db_path="gantt.db")
        self.current_tab = None
        self.selected_tab = "Calendar"  # Track the selected tab
        self.sidebar_buttons = {}  # Store references to sidebar buttons
        self.init_ui()
        # Open in full screen after login
        self.showMaximized()

    def init_ui(self):
        self.setStyleSheet(STYLESHEET)

        # Top Bar
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)

        # Left side of top bar (logo and Construction Manager)
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logos/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(173, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("Guth")
            logo_label.setStyleSheet("color: #38a169; font-size: 18px; font-weight: bold; font-family: 'Roboto';")
        top_layout.addWidget(logo_label)

        dashboard_label = QLabel("Construction Manager")
        dashboard_label.setObjectName("topBarLabel")
        top_layout.addWidget(dashboard_label)

        top_layout.addStretch()

        # Right side of top bar
        user_label = QLabel(f"{self.user_info['username']}")
        user_label.setObjectName("topBarLabel")
        top_layout.addWidget(user_label)

        # Add a separator line between cm_user and Guth South Africa
        separator = QLabel("|")
        separator.setStyleSheet("color: #e2e8f0; font-size: 14px; font-family: 'Roboto'; margin: 0 5px;")
        top_layout.addWidget(separator)

        company_label = QLabel("Guth South Africa")
        company_label.setObjectName("topBarLabel")
        top_layout.addWidget(company_label)

        add_button = QPushButton("+")
        add_button.setStyleSheet("color: #38a169; font-size: 24px; font-weight: bold; background-color: transparent; border: none; padding: 5px 10px;")
        add_button.clicked.connect(self.show_add_menu)
        top_layout.addWidget(add_button)

        help_button = QPushButton("Help")
        help_button.setStyleSheet("background-color: black; color: white; border-radius: 4px; padding: 5px 10px;")
        top_layout.addWidget(help_button)

        # Main Layout
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(top_bar)

        content_layout = QHBoxLayout()

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        # Sidebar Navigation
        for item in [("Dashboard", "🏠"), ("Calendar", "📅"), ("Projects", "📁"), 
                     ("Artisans", "👥"), ("Reports", "📊"), ("Timesheets", "⏰"), 
                     ("Documents", "📜"), ("Goals", "🎯")]:
            btn = QPushButton(f"{item[1]} {item[0]}")
            btn.setObjectName("sidebarButton")
            # Set initial style for the selected tab
            if item[0] == self.selected_tab:
                btn.setStyleSheet("""
                    QPushButton#sidebarButton {
                        background-color: #2E3A3B;
                        color: white;
                        padding: 10px;
                        border: none;
                        text-align: left;
                        font-size: 14px;
                        font-family: 'Roboto';
                    }
                """)
            btn.clicked.connect(lambda checked, text=item[0]: self.navigate_to(text))
            self.sidebar_buttons[item[0]] = btn  # Store the button reference
            sidebar_layout.addWidget(btn)

        # Artisans List
        self.artisans_tree = QTreeWidget()
        self.artisans_tree.setHeaderHidden(True)
        artisans_item = QTreeWidgetItem(self.artisans_tree, ["👥 Artisans"])
        self.load_artisans_in_sidebar(artisans_item)
        self.artisans_tree.itemClicked.connect(self.on_artisan_item_clicked)
        self.artisans_tree.setDragEnabled(True)
        sidebar_layout.addWidget(self.artisans_tree)

        sidebar_layout.addStretch()
        logout_button = QPushButton("🚪 Logout")
        logout_button.setObjectName("sidebarButton")
        logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_button)

        content_layout.addWidget(sidebar)

        # Content Area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        content_layout.addWidget(self.content_widget)

        main_layout.addLayout(content_layout)

        # Footer
        footer_label = QLabel("Build 1.0.0 | Copyright Guth South Africa")
        footer_label.setStyleSheet("color: #2d3748; font-size: 10px; font-family: 'Roboto'; text-align: center; padding: 5px;")
        main_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(central_widget)

        # Load the default tab (Calendar)
        self.navigate_to("Calendar")

    def show_add_menu(self):
        menu = QMenu(self)
        add_artisan_action = menu.addAction("Add Artisan")
        add_project_action = menu.addAction("Add Project")
        action = menu.exec(self.mapToGlobal(self.sender().pos()))
        if action == add_artisan_action:
            self.add_item("Artisan")
        elif action == add_project_action:
            self.add_item("Project")

    def add_item(self, item_type):
        dialog = AddItemDialog(item_type, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if item_type == "Artisan":
                    artisan_id = self.db.add_artisan(
                        name=data["name"],
                        skill=data["skill"],
                        availability=data["availability"]
                    )
                    QMessageBox.information(self, "Success", f"Artisan {data['name']} added with ID {artisan_id}")
                elif item_type == "Project":
                    project_id = self.db.add_project(
                        name=data["name"],
                        start_date=data["start_date"],
                        end_date=data["end_date"],
                        status=data["status"],
                        job_number=data["job_number"],
                        description=data["description"]
                    )
                    QMessageBox.information(self, "Success", f"Project {data['name']} added with ID {project_id}")
                self.load_artisans_in_sidebar(QTreeWidgetItem(self.artisans_tree, ["👥 Artisans"]))
                if self.current_tab:
                    self.current_tab.load_gantt_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_artisans_in_sidebar(self, parent_item):
        self.artisans_tree.clear()
        artisans_item = QTreeWidgetItem(self.artisans_tree, ["👥 Artisans"])
        artisans = self.db.get_artisans()
        for artisan in artisans:
            item = QTreeWidgetItem(artisans_item)
            item.setText(0, artisan[1])
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "artisan", "id": artisan[0]})

    def on_artisan_item_clicked(self, item, column):
        if item.data(0, Qt.ItemDataRole.UserRole):
            drag_data = item.data(0, Qt.ItemDataRole.UserRole)
            if self.current_tab and hasattr(self.current_tab, 'set_drag_data'):
                self.current_tab.set_drag_data(drag_data)

    def navigate_to(self, section):
        # Update the selected tab and button styles
        self.selected_tab = section
        for tab_name, btn in self.sidebar_buttons.items():
            if tab_name == section:
                btn.setStyleSheet("""
                    QPushButton#sidebarButton {
                        background-color: #2E3A3B;
                        color: white;
                        padding: 10px;
                        border: none;
                        text-align: left;
                        font-size: 14px;
                        font-family: 'Roboto';
                    }
                    QPushButton#sidebarButton:hover {
                        background-color: #2E3A3B;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton#sidebarButton {
                        background-color: transparent;
                        color: white;
                        padding: 10px;
                        border: none;
                        text-align: left;
                        font-size: 14px;
                        font-family: 'Roboto';
                    }
                    QPushButton#sidebarButton:hover {
                        background-color: #2E3A3B;
                    }
                """)

        # Navigate to the selected tab
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if section == "Dashboard":
            self.current_tab = DashboardTab(self.db, self)
        elif section == "Calendar":
            self.current_tab = CalendarTab(self.db, self)
        elif section == "Projects":
            self.current_tab = ProjectsTab(self.db, self)
        elif section == "Artisans":
            self.current_tab = ArtisansTab(self.db, self)
        elif section == "Reports":
            self.current_tab = ReportsTab(self.db, self)
        elif section == "Timesheets":
            self.current_tab = TimesheetsTab(self.db, self)
        elif section == "Documents":
            self.current_tab = DocumentsTab(self.db, self)
        elif section == "Goals":
            self.current_tab = GoalsTab(self.db, self)
        elif section == "Feedback":
            self.current_tab = FeedbackTab(self.db, self)

        self.content_layout.addWidget(self.current_tab)

    def logout(self):
        self.db.close()
        self.close()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def closeEvent(self, event):
        self.db.close()
        event.accept()