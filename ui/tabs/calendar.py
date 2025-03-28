# ui/tabs/calendar.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, 
                             QFormLayout, QComboBox, QDialog, QDialogButtonBox, QSizePolicy, QTreeWidget, QTreeWidgetItem, QMenu,
                             QCalendarWidget, QLabel, QListWidget, QListWidgetItem, QScrollArea)
from PyQt6.QtCore import Qt, QRectF, QDate, QPoint, QTimer
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

# South African Public Holidays for 2025 (hardcoded)
SA_PUBLIC_HOLIDAYS_2025 = [
    "2025-01-01",  # New Year's Day
    "2025-03-21",  # Human Rights Day
    "2025-04-18",  # Good Friday
    "2025-04-21",  # Family Day
    "2025-04-28",  # Freedom Day (observed)
    "2025-05-01",  # Workers' Day
    "2025-06-16",  # Youth Day
    "2025-08-11",  # National Women's Day (observed)
    "2025-09-24",  # Heritage Day
    "2025-12-16",  # Day of Reconciliation
    "2025-12-25",  # Christmas Day
    "2025-12-26",  # Day of Goodwill
]

# Expanded list of contrasting colors for project bars
PROJECT_COLORS = [
    '#FF6347', '#4682B4', '#32CD32', '#FFD700', '#6A5ACD', '#FF4500', '#20B2AA', '#DAA520', 
    '#9932CC', '#00CED1', '#FF69B4', '#8B008B', '#00FF7F', '#B22222', '#7FFF00', '#DC143C', 
    '#00FA9A', '#4169E1', '#FF1493', '#ADFF2F', '#FF8C00', '#8A2BE2', '#228B22', '#FF00FF', 
    '#1E90FF', '#FF4040', '#2E8B57', '#BA55D3', '#00BFFF', '#FF7F50'
]

# Customizable colors for styling
GRID_CELL_COLOR = '#FFFFFF'  # Default grid cell background (white)
ALTERNATING_DAY_COLOR = '#E8ECEF'  # Lighter gray for alternating days
ALTERNATING_ROW_COLOR = '#F5F5F5'  # Very light gray for alternating rows
WEEKEND_COLOR = '#B0C4DE'  # Light steel blue for weekends
HOLIDAY_COLOR = '#87CEFA'  # Light sky blue for holidays
LEGEND_BG_COLOR = '#F0F0F0'  # Light gray background for legend
LEGEND_TEXT_COLOR = '#333333'  # Dark gray text for legend

class DatePickerDialog(QDialog):
    def __init__(self, initial_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.initial_date = initial_date
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create a calendar widget
        self.calendar = QCalendarWidget()
        # Set the initial date to today's date
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        
        layout.addWidget(self.calendar)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_date(self):
        selected_date = self.calendar.selectedDate()
        return selected_date.toString("yyyy-MM-dd")

class NewProjectDialog(QDialog):
    def __init__(self, artisans, start_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start New Project")
        self.artisans = artisans
        self.start_date = start_date
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.job_name_input = QLineEdit()
        self.job_number_input = QLineEdit()
        self.description_input = QLineEdit()
        
        # Start date button
        self.start_date_button = QPushButton(self.start_date)
        self.start_date_button.clicked.connect(self.select_start_date)
        
        # End date button (default to 5 days after start date)
        self.end_date = (datetime.strptime(self.start_date, "%Y-%m-%d") + timedelta(days=5)).strftime("%Y-%m-%d")
        self.end_date_button = QPushButton(self.end_date)
        self.end_date_button.clicked.connect(self.select_end_date)
        
        self.artisans_combo = QComboBox()
        self.artisans_combo.addItem("Select Artisan", None)
        for artisan in self.artisans:
            self.artisans_combo.addItem(artisan[1], artisan[0])
        self.additional_artisans_combo = QComboBox()
        self.additional_artisans_combo.addItem("Select Additional Artisan (Optional)", None)
        for artisan in self.artisans:
            self.additional_artisans_combo.addItem(artisan[1], artisan[0])
        self.team_name_input = QLineEdit()
        self.team_name_input.setEnabled(False)
        self.artisans_combo.currentIndexChanged.connect(self.toggle_team_name)
        self.additional_artisans_combo.currentIndexChanged.connect(self.toggle_team_name)

        layout.addRow("Job Name:", self.job_name_input)
        layout.addRow("Job Number:", self.job_number_input)
        layout.addRow("Job Description:", self.description_input)
        layout.addRow("Start Date:", self.start_date_button)
        layout.addRow("End Date:", self.end_date_button)
        layout.addRow("Assign Artisan:", self.artisans_combo)
        layout.addRow("Additional Artisan:", self.additional_artisans_combo)
        layout.addRow("Team Name (if multiple artisans):", self.team_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def toggle_team_name(self):
        if self.artisans_combo.currentData() and self.additional_artisans_combo.currentData():
            self.team_name_input.setEnabled(True)
        else:
            self.team_name_input.setEnabled(False)

    def select_start_date(self):
        dialog = DatePickerDialog(self.start_date, self)
        if dialog.exec():
            self.start_date = dialog.get_selected_date()
            self.start_date_button.setText(self.start_date)

    def select_end_date(self):
        dialog = DatePickerDialog(self.end_date, self)
        if dialog.exec():
            self.end_date = dialog.get_selected_date()
            self.end_date_button.setText(self.end_date)

    def get_data(self):
        return {
            "job_name": self.job_name_input.text().strip(),
            "job_number": self.job_number_input.text().strip(),
            "description": self.description_input.text().strip(),
            "start_date": self.start_date_button.text().strip(),
            "end_date": self.end_date_button.text().strip(),
            "artisan_id": self.artisans_combo.currentData(),
            "additional_artisan_id": self.additional_artisans_combo.currentData(),
            "team_name": self.team_name_input.text().strip() if self.team_name_input.isEnabled() else None
        }

class EditProjectDialog(QDialog):
    def __init__(self, project, artisans, assigned_artisans, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project")
        self.project = project
        self.artisans = artisans
        self.assigned_artisans = assigned_artisans  # List of (artisan_id, artisan_name)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        
        # Project details
        self.job_name_input = QLineEdit(self.project[1])
        self.job_number_input = QLineEdit(self.project[5])
        self.description_input = QLineEdit(self.project[6])
        
        # Start date button
        self.start_date_button = QPushButton(self.project[2])
        self.start_date_button.clicked.connect(self.select_start_date)
        
        # End date button
        self.end_date_button = QPushButton(self.project[3])
        self.end_date_button.clicked.connect(self.select_end_date)

        # Assigned artisans list
        self.assigned_artisans_list = QListWidget()
        for artisan_id, artisan_name in self.assigned_artisans:
            item = QListWidgetItem(artisan_name)
            item.setData(Qt.ItemDataRole.UserRole, artisan_id)
            self.assigned_artisans_list.addItem(item)

        # Button to remove selected artisan
        self.remove_artisan_button = QPushButton("Remove Selected Artisan")
        self.remove_artisan_button.clicked.connect(self.remove_artisan)

        # Combo box to add new artisans
        self.add_artisan_combo = QComboBox()
        self.add_artisan_combo.addItem("Select Artisan to Add", None)
        for artisan in self.artisans:
            # Only add artisans that are not already assigned
            if artisan[0] not in [a[0] for a in self.assigned_artisans]:
                self.add_artisan_combo.addItem(artisan[1], artisan[0])
        self.add_artisan_combo.currentIndexChanged.connect(self.add_artisan)

        layout.addRow("Job Name:", self.job_name_input)
        layout.addRow("Job Number:", self.job_number_input)
        layout.addRow("Job Description:", self.description_input)
        layout.addRow("Start Date:", self.start_date_button)
        layout.addRow("End Date:", self.end_date_button)
        layout.addRow("Assigned Artisans:", self.assigned_artisans_list)
        layout.addRow(self.remove_artisan_button)
        layout.addRow("Add Artisan:", self.add_artisan_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def select_start_date(self):
        dialog = DatePickerDialog(self.start_date_button.text(), self)
        if dialog.exec():
            self.start_date_button.setText(dialog.get_selected_date())

    def select_end_date(self):
        dialog = DatePickerDialog(self.end_date_button.text(), self)
        if dialog.exec():
            self.end_date_button.setText(dialog.get_selected_date())

    def remove_artisan(self):
        selected_items = self.assigned_artisans_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an artisan to remove.")
            return
        for item in selected_items:
            artisan_id = item.data(Qt.ItemDataRole.UserRole)
            # Remove from the list
            self.assigned_artisans_list.takeItem(self.assigned_artisans_list.row(item))
            # Add back to the combo box
            for artisan in self.artisans:
                if artisan[0] == artisan_id:
                    self.add_artisan_combo.addItem(artisan[1], artisan[0])
                    break

    def add_artisan(self):
        artisan_id = self.add_artisan_combo.currentData()
        if artisan_id:
            # Find the artisan name
            artisan_name = self.add_artisan_combo.currentText()
            # Add to the assigned artisans list
            item = QListWidgetItem(artisan_name)
            item.setData(Qt.ItemDataRole.UserRole, artisan_id)
            self.assigned_artisans_list.addItem(item)
            # Remove from the combo box
            self.add_artisan_combo.removeItem(self.add_artisan_combo.currentIndex())
            # Reset the combo box to "Select Artisan to Add"
            self.add_artisan_combo.setCurrentIndex(0)

    def get_data(self):
        # Get the updated list of assigned artisans
        assigned_artisans = []
        for i in range(self.assigned_artisans_list.count()):
            item = self.assigned_artisans_list.item(i)
            artisan_id = item.data(Qt.ItemDataRole.UserRole)
            assigned_artisans.append(artisan_id)
        
        return {
            "job_name": self.job_name_input.text().strip(),
            "job_number": self.job_number_input.text().strip(),
            "description": self.description_input.text().strip(),
            "start_date": self.start_date_button.text().strip(),
            "end_date": self.end_date_button.text().strip(),
            "assigned_artisans": assigned_artisans
        }

class NewAssignmentDialog(QDialog):
    def __init__(self, artisan_id, project_id, projects, artisans, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Assignment")
        self.artisan_id = artisan_id
        self.project_id = project_id
        self.projects = projects
        self.artisans = artisans
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.project_combo = QComboBox()
        for project in self.projects:
            self.project_combo.addItem(f"{project[1]} (ID: {project[0]})", project[0])
        self.project_combo.setCurrentText(f"{self.projects[self.project_id][1]} (ID: {self.project_id})")
        self.job_number_input = QLineEdit()
        self.description_input = QLineEdit()
        self.start_date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.days_input = QLineEdit("5")
        self.artisans_combo = QComboBox()
        for artisan in self.artisans:
            self.artisans_combo.addItem(artisan[1], artisan[0])

        layout.addRow("Project:", self.project_combo)
        layout.addRow("Job Number:", self.job_number_input)
        layout.addRow("Job Description:", self.description_input)
        layout.addRow("Start Date:", self.start_date_input)
        layout.addRow("Number of Days:", self.days_input)
        layout.addRow("Add Another Artisan:", self.artisans_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "artisan_id": self.artisan_id,
            "project_id": self.project_combo.currentData(),
            "job_number": self.job_number_input.text().strip(),
            "description": self.description_input.text().strip(),
            "start_date": self.start_date_input.text().strip(),
            "days": self.days_input.text().strip(),
            "additional_artisan_id": self.artisans_combo.currentData()
        }

class TeamAssignmentDialog(QDialog):
    def __init__(self, artisan_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Team Assignment")
        self.artisan_id = artisan_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Add artisan to existing project?"))
        self.team_radio = QComboBox()
        self.team_radio.addItems(["Create Team", "Separate Assignment"])
        layout.addWidget(self.team_radio)
        self.team_name_input = QLineEdit()
        layout.addWidget(QLabel("Team Name (if creating team):"))
        layout.addWidget(self.team_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "choice": self.team_radio.currentText(),
            "team_name": self.team_name_input.text().strip() if self.team_radio.currentText() == "Create Team" else None
        }

class ProjectActionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Actions")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose an action for the project:"))

        self.edit_button = QPushButton("Edit Project")
        self.edit_button.clicked.connect(self.accept_edit)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Project")
        self.delete_button.clicked.connect(self.accept_delete)
        layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    def accept_edit(self):
        self.done(1)  # Return 1 for Edit

    def accept_delete(self):
        self.done(2)  # Return 2 for Delete

class CalendarTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.date_range = 42  # 6 weeks
        self.start_date = datetime.now()
        self.drag_data = None
        self.selected_bar = None
        self.drag_start_x = None
        self.drag_start_width = None
        self.drag_edge = None  # 'left' or 'right'
        self.holidays = self.fetch_holidays()
        self.project_color_index = 0  # Track the color index for projects
        self.project_colors = {}  # Map project IDs to colors
        self.artisan_images = {}  # Cache for artisan images
        self.team_names = {}  # Cache for team names
        self.project_assignments = {}  # Cache for project assignments
        self.y_pos = None  # Cache for y-positions
        self.y_pos_centered = None  # Cache for centered y-positions
        self.project_action_dialog = ProjectActionDialog(self)
        # Timer for debouncing redraws during drag
        self.redraw_timer = QTimer(self)
        self.redraw_timer.setSingleShot(True)
        self.redraw_timer.timeout.connect(self.deferred_redraw)
        self.redraw_pending = False
        # Scroll position
        self.scroll_offset = 0
        self.visible_rows = 10  # Number of visible rows
        self.init_ui()

    def fetch_holidays(self):
        return SA_PUBLIC_HOLIDAYS_2025

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 20)
        layout.setSpacing(5)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search by teams, projects, or artisans...")
        controls_layout.addWidget(self.search_input)

        controls_layout.addStretch()

        prev_button = QPushButton("Previous 6 Weeks")
        prev_button.clicked.connect(self.prev_date_range)
        controls_layout.addWidget(prev_button)

        controls_layout.addSpacing(20)

        next_button = QPushButton("Next 6 Weeks")
        next_button.clicked.connect(self.next_date_range)
        controls_layout.addWidget(next_button)

        controls_layout.addSpacing(20)

        sync_button = QPushButton("Sync with Outlook")
        sync_button.clicked.connect(self.sync_outlook)
        controls_layout.addWidget(sync_button)

        layout.addLayout(controls_layout)

        # Scroll area for the Gantt chart
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        self.gantt_widget = QWidget()
        self.gantt_canvas = FigureCanvas(plt.Figure(figsize=(24, 16)))
        self.gantt_canvas.setStyleSheet("background-color: #FFFFFF;")
        self.gantt_layout = QVBoxLayout(self.gantt_widget)
        self.gantt_layout.addWidget(self.gantt_canvas)
        self.scroll_area.setWidget(self.gantt_widget)

        layout.addWidget(self.scroll_area, stretch=1)

        # Chatbot Icon (Smaller, Circular Button, Bottom Right)
        self.chatbot_button = QPushButton("💬")
        self.chatbot_button.setObjectName("chatbotButton")
        self.chatbot_button.setStyleSheet("""
            QPushButton#chatbotButton {
                background-color: #007AFF;
                color: white;
                border-radius: 15px;
                width: 30px;
                height: 30px;
                font-size: 14px;
                position: absolute;
                bottom: 10px;
                right: 10px;
                padding: 0px;
                border: none;
            }
            QPushButton#chatbotButton:hover {
                background-color: #005BB5;
            }
        """)
        self.chatbot_button.clicked.connect(self.open_chatbot)
        layout.addWidget(self.chatbot_button)

        self.load_gantt_data()

        self.gantt_canvas.mpl_connect('button_press_event', self.on_press)
        self.gantt_canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.gantt_canvas.mpl_connect('button_release_event', self.on_release)

    def on_scroll(self, value):
        self.scroll_offset = value // (self.block_height + self.row_gap)
        self.update_gantt_chart(self.assignments, self.projects, self.artisans, self.teams)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        new_project_action = context_menu.addAction("Start New Project")
        action = context_menu.exec(event.globalPos())
        if action == new_project_action:
            xdata = event.x()
            inv = self.gantt_canvas.figure.axes[0].transData.inverted()
            x, _ = inv.transform((xdata, 0))
            clicked_date = mdates.num2date(x).replace(tzinfo=None)
            self.start_new_project(clicked_date)

    def on_press(self, event):
        if event.button != 1 or event.inaxes != self.gantt_canvas.figure.axes[0]:
            return
        for bar, assignment, project_idx, start, end in self.bars:
            if bar.contains(event)[0]:
                if event.dblclick:
                    self.on_double_click(project_idx, assignment)
                else:
                    self.selected_bar = {"bar": bar, "assignment": assignment, "project_idx": project_idx, "start": start, "end": end}
                    self.drag_start_x = event.xdata
                    self.drag_start_width = bar.get_width()
                    bar_x = bar.get_x()
                    bar_width = bar.get_width()
                    self.drag_edge = 'left' if abs(event.xdata - bar_x) < abs(event.xdata - (bar_x + bar_width)) else 'right'
                break

    def on_double_click(self, project_idx, assignment):
        result = self.project_action_dialog.exec()
        if result == 1:  # Edit Project
            self.edit_project(project_idx, assignment)
        elif result == 2:  # Delete Project
            self.delete_project(project_idx, assignment)

    def on_motion(self, event):
        if not self.selected_bar or not event.xdata:
            return
        delta = event.xdata - self.drag_start_x
        bar = self.selected_bar["bar"]
        if self.drag_edge == 'left':
            new_x = bar.get_x() + delta
            new_width = self.drag_start_width - delta
            if new_width > 0:
                bar.set_x(new_x)
                bar.set_width(new_width)
        else:
            new_width = max(1, self.drag_start_width + delta)
            bar.set_width(new_width)
        if not self.redraw_timer.isActive():
            self.redraw_timer.start(50)
        self.redraw_pending = True

    def deferred_redraw(self):
        if self.redraw_pending:
            self.gantt_canvas.draw()
            self.redraw_pending = False

    def on_release(self, event):
        if self.selected_bar:
            bar = self.selected_bar["bar"]
            assignment = self.selected_bar["assignment"]
            start_date = datetime.fromordinal(int(bar.get_x())).strftime("%Y-%m-%d")
            end_date = (datetime.fromordinal(int(bar.get_x())) + 
                        timedelta(days=int(bar.get_width()) - 1)).strftime("%Y-%m-%d")
            try:
                self.db.update_assignment(assignment[0], start_date, end_date)
                self.load_gantt_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            self.selected_bar = None
            self.drag_edge = None
        self.drag_data = None

    def edit_project(self, project_idx, assignment):
        project_id = assignment[2]
        project = self.db.cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        assigned_artisans = self.db.cursor.execute(
            "SELECT a.id, a.name FROM artisans a JOIN assignments ass ON a.id = ass.artisan_id WHERE ass.project_id = ?",
            (project_id,)
        ).fetchall()
        dialog = EditProjectDialog(project, self.db.get_artisans(), assigned_artisans, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if not data["job_name"]:
                    raise ValueError("Job name is required")
                if not data["start_date"] or not data["end_date"]:
                    raise ValueError("Start date and end date are required")
                start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
                if end_date < start_date:
                    raise ValueError("End date must be after start date")
                self.db.cursor.execute(
                    "UPDATE projects SET name = ?, start_date = ?, end_date = ?, job_number = ?, description = ? WHERE id = ?",
                    (data["job_name"], data["start_date"], data["end_date"], data["job_number"], data["description"], project_id)
                )
                self.db.cursor.execute("DELETE FROM assignments WHERE project_id = ?", (project_id,))
                for artisan_id in data["assigned_artisans"]:
                    self.db.add_assignment(artisan_id, project_id, data["start_date"], data["end_date"])
                self.db.conn.commit()
                QMessageBox.information(self, "Success", f"Project {data['job_name']} updated successfully")
                self.load_gantt_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_project(self, project_idx, assignment):
        project_id = assignment[2]
        project = self.db.cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete project '{project[1]}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.cursor.execute("DELETE FROM assignments WHERE project_id = ?", (project_id,))
            self.db.cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            self.db.conn.commit()
            QMessageBox.information(self, "Success", f"Project '{project[1]}' deleted successfully")
            self.load_gantt_data()

    def start_new_project(self, start_date):
        dialog = NewProjectDialog(self.db.get_artisans(), start_date.strftime("%Y-%m-%d"), self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if not data["job_name"]:
                    raise ValueError("Job name is required")
                if not data["artisan_id"]:
                    raise ValueError("At least one artisan must be assigned")
                if not data["start_date"] or not data["end_date"]:
                    raise ValueError("Start date and end date are required")
                start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
                if end_date < start_date:
                    raise ValueError("End date must be after start date")
                project_id = self.db.add_project(
                    name=data["job_name"],
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    status="Active",
                    job_number=data["job_number"],
                    description=data["description"]
                )
                artisan_ids = [data["artisan_id"]]
                if data["additional_artisan_id"]:
                    artisan_ids.append(data["additional_artisan_id"])
                team_id = None
                if len(artisan_ids) > 1 and data["team_name"]:
                    team_name = data["team_name"]
                    team_id = self.db.add_team(team_name)
                for artisan_id in artisan_ids:
                    self.db.add_assignment(artisan_id, project_id, data["start_date"], data["end_date"])
                    if team_id:
                        self.db.update_artisan_team(artisan_id, team_id)
                QMessageBox.information(self, "Success", f"Project {data['job_name']} created with ID {project_id}")
                self.load_gantt_data()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_gantt_data(self):
        self.projects = [p for p in self.db.get_projects() if p[4] == "Active"]
        self.assignments = self.db.get_assignments()
        self.artisans = {a[0]: (a[1], a[5]) for a in self.db.get_artisans()}
        self.teams = {t[0]: t[1] for t in self.db.cursor.execute("SELECT id, name FROM teams").fetchall()}
        # Cache project assignments and team names
        self.project_assignments = {p[0]: [a for a in self.assignments if a[2] == p[0]] for p in self.projects}
        self.team_names = {}
        for p in self.projects:
            project_id = p[0]
            team_id = self.db.cursor.execute(
                "SELECT team_id FROM artisans WHERE id IN (SELECT artisan_id FROM assignments WHERE project_id = ?)",
                (project_id,)
            ).fetchone()
            self.team_names[project_id] = self.teams.get(team_id[0], "No Team Facetools") if team_id and team_id[0] else "No Team"
        # Cache artisan images
        for artisan_id, (name, picture_path) in self.artisans.items():
            try:
                self.artisan_images[artisan_id] = mpimg.imread(picture_path)
            except FileNotFoundError:
                self.artisan_images[artisan_id] = None
        self.update_gantt_chart(self.assignments, self.projects, self.artisans, self.teams)

    def update_gantt_chart(self, assignments, projects, artisans, teams):
        self.gantt_canvas.figure.clear()
        ax = self.gantt_canvas.figure.add_subplot(111)

        # Date range
        end_date = self.start_date + timedelta(days=self.date_range - 1)
        date_list = [self.start_date + timedelta(days=x) for x in range(self.date_range)]
        date_ordinals = np.array([d.toordinal() for d in date_list])

        # Add month and year above the dates with reduced padding
        month_year = self.start_date.strftime("%B %Y")
        ax.set_title(month_year, fontsize=12, pad=15, fontfamily='Roboto', fontweight='bold')  # Reduced pad from 30 to 15

        # Define block dimensions
        self.block_height = 22
        self.block_width = 0.8
        self.row_gap = 3
        num_rows = max(len(projects), self.visible_rows)  # Total number of rows needed

        # Precompute y-positions for all rows
        self.y_pos = [(num_rows - 1 - i) * (self.block_height + self.row_gap) for i in range(num_rows)]
        self.y_pos_centered = [y + self.block_height / 2 for y in self.y_pos]

        # Determine visible rows based on scroll position
        start_row = self.scroll_offset
        end_row = min(start_row + self.visible_rows, num_rows)
        visible_y_pos = self.y_pos[start_row:end_row]
        visible_y_pos_centered = self.y_pos_centered[start_row:end_row]

        # Create grid cells using PatchCollection
        grid_cells = []
        alternating_cells = []
        weekend_cells = []
        holiday_cells = []
        day_numbers = []
        row_backgrounds = []
        for row_idx in range(start_row, end_row):
            y = self.y_pos[row_idx]
            # Add alternating row background
            if row_idx % 2 == 0:
                row_background = Rectangle((date_ordinals[0] - 0.5, y), 
                                           len(date_list), self.block_height, 
                                           facecolor=ALTERNATING_ROW_COLOR, zorder=0)
                row_backgrounds.append(row_background)
            for i, d in enumerate(date_list):
                ordinal = d.toordinal()
                # Base grid cell (no grid lines)
                cell = Rectangle((ordinal - 0.5, y), self.block_width, self.block_height, 
                                 edgecolor='none', facecolor=GRID_CELL_COLOR)
                grid_cells.append(cell)
                # Day number
                day_numbers.append((ordinal, y + self.block_height - 5, d.strftime("%d")))
                # Alternating background for days
                if i % 2 == 0:
                    alternating_cells.append(Rectangle((ordinal - 0.5, y), self.block_width, self.block_height))
                # Weekend background
                if d.weekday() >= 5:
                    weekend_cells.append(Rectangle((ordinal - 0.5, y), self.block_width, self.block_height))
                # Holiday background
                if d.strftime("%Y-%m-%d") in self.holidays:
                    holiday_cells.append(Rectangle((ordinal - 0.5, y), self.block_width, self.block_height))

        # Draw row backgrounds
        if row_backgrounds:
            row_bg_collection = PatchCollection(row_backgrounds, match_original=True, zorder=0)
            ax.add_collection(row_bg_collection)

        # Draw grid cells using PatchCollection
        grid_collection = PatchCollection(grid_cells, edgecolor='none', facecolor=GRID_CELL_COLOR, zorder=1)
        ax.add_collection(grid_collection)

        # Draw alternating day backgrounds
        if alternating_cells:
            alt_collection = PatchCollection(alternating_cells, facecolor=ALTERNATING_DAY_COLOR, alpha=0.3, zorder=2)
            ax.add_collection(alt_collection)

        # Draw weekend backgrounds
        if weekend_cells:
            weekend_collection = PatchCollection(weekend_cells, facecolor=WEEKEND_COLOR, alpha=0.5, zorder=3)
            ax.add_collection(weekend_collection)

        # Draw holiday backgrounds
        if holiday_cells:
            holiday_collection = PatchCollection(holiday_cells, facecolor=HOLIDAY_COLOR, alpha=0.5, zorder=3)
            ax.add_collection(holiday_collection)

        # Draw day numbers
        for x, y, text in day_numbers:
            ax.text(x, y, text, fontsize=8, fontfamily='Roboto', color='black', ha='center', va='top', zorder=4)

        # Add days of the week at the bottom
        ax.set_xticks(date_ordinals)
        ax.set_xticklabels([d.strftime("%a")[0:2].capitalize() for d in date_list], 
                           fontsize=8, fontfamily='Roboto', rotation=0)
        ax.tick_params(axis='x', which='major', pad=10)
        ax.xaxis.set_minor_locator(mdates.DayLocator())

        # Projects on y-axis
        y_labels = [""] * self.visible_rows
        for project_idx in range(start_row, min(end_row, len(projects))):
            visible_idx = project_idx - start_row
            project = projects[project_idx]
            project_id = project[0]
            project_assignments = self.project_assignments.get(project_id, [])
            artisans_in_project = [artisans[a[1]][0] for a in project_assignments]
            team_name = self.team_names.get(project_id, "No Team")
            y_labels[visible_idx] = f"{project[1]}\n{team_name}: {', '.join(artisans_in_project)}"
        ax.set_yticks(visible_y_pos_centered)
        ax.set_yticklabels(y_labels, fontsize=9, fontfamily='Roboto', fontweight='bold', va='center')  # Increased fontsize from 7 to 9

        # Adjust the margins
        self.gantt_canvas.figure.subplots_adjust(left=0.25, bottom=0.2, top=0.92)

        # Draw project bars
        self.bars = []
        for project_idx in range(start_row, min(end_row, len(projects))):
            visible_idx = project_idx - start_row
            project = projects[project_idx]
            project_id = project[0]
            project_assignments = self.project_assignments.get(project_id, [])
            if project_id not in self.project_colors:
                color = PROJECT_COLORS[self.project_color_index % len(PROJECT_COLORS)]
                self.project_colors[project_id] = color
                self.project_color_index += 1
            project_color = self.project_colors[project_id]
            y = visible_y_pos[visible_idx]
            for idx, assignment in enumerate(project_assignments):
                start = datetime.strptime(assignment[3], "%Y-%m-%d")
                end = datetime.strptime(assignment[4], "%Y-%m-%d")
                start_ordinal = max(start.toordinal(), self.start_date.toordinal())
                end_ordinal = min(end.toordinal(), end_date.toordinal())
                if start_ordinal <= end_ordinal:
                    bar_width = end_ordinal - start_ordinal + 1
                    bar = Rectangle((start_ordinal - 0.5, y), bar_width, self.block_height, 
                                    color=project_color, alpha=0.4, zorder=5)
                    ax.add_patch(bar)
                    gradient = ax.fill_betweenx([y, y + self.block_height], 
                                                start_ordinal - 0.5, start_ordinal + bar_width - 0.5, 
                                                color=project_color, alpha=0.2, zorder=5)
                    self.bars.append((bar, assignment, project_idx, start, end))
                for i, artisan in enumerate([(a[1], artisans[a[1]][1]) for a in project_assignments]):
                    artisan_id, picture_path = artisan
                    img = self.artisan_images.get(artisan_id)
                    if img is not None:
                        imagebox = OffsetImage(img, zoom=0.03)
                        ab = AnnotationBbox(imagebox, (start.toordinal() + (i * 0.4), y + self.block_height - 5), frameon=False, zorder=6)
                        ax.add_artist(ab)
                    else:
                        ax.scatter(start.toordinal() + (i * 0.4), y + self.block_height - 5, s=30, color=f"C{i}", marker='o', zorder=6)

        ax.set_ylim(min(visible_y_pos) - self.row_gap, max(visible_y_pos) + self.block_height + self.row_gap)
        ax.set_xlim(self.start_date.toordinal() - 1, end_date.toordinal() + 1)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=WEEKEND_COLOR, alpha=0.5, label='Weekends'),
            Patch(facecolor=HOLIDAY_COLOR, alpha=0.5, label='Public Holidays')
        ]
        ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=2, 
                  prop={'family': 'Roboto', 'size': 8}, 
                  facecolor=LEGEND_BG_COLOR, edgecolor='none', 
                  labelcolor=LEGEND_TEXT_COLOR)

        self.gantt_canvas.draw()

    def set_drag_data(self, drag_data):
        self.drag_data = drag_data

    def prev_date_range(self):
        self.start_date -= timedelta(days=self.date_range)
        self.holidays = self.fetch_holidays()
        self.load_gantt_data()

    def next_date_range(self):
        self.start_date += timedelta(days=self.date_range)
        self.holidays = self.fetch_holidays()
        self.load_gantt_data()

    def sync_outlook(self):
        QMessageBox.information(self, "Outlook Sync", "Outlook sync functionality is not yet implemented.")

    def open_chatbot(self):
        QMessageBox.information(self, "Chatbot", "AI chatbot functionality is not yet implemented.")