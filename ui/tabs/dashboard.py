# ui/tabs/dashboard.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QAbstractItemView, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QColor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class TimelineEntry(QWidget):
    def __init__(self, action, details, timestamp, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Icon
        icon_label = QLabel()
        icon = "📝" if "Added" in action else "🔄" if "Updated" in action else "📅"
        icon_label.setText(icon)
        icon_label.setStyleSheet("font-size: 20px; margin-right: 10px;")
        layout.addWidget(icon_label)

        # Details
        details_layout = QVBoxLayout()
        action_label = QLabel(action)
        action_label.setStyleSheet("font-size: 14px; font-weight: bold; font-family: 'Roboto'; color: #2d3748;")
        details_layout.addWidget(action_label)

        details_label = QLabel(details)
        details_label.setStyleSheet("font-size: 12px; font-family: 'Roboto'; color: #4a5568;")
        details_layout.addWidget(details_label)

        timestamp_label = QLabel(timestamp)
        timestamp_label.setStyleSheet("font-size: 10px; font-family: 'Roboto'; color: #718096;")
        details_layout.addWidget(timestamp_label)

        layout.addLayout(details_layout)

        # Separator line
        self.setStyleSheet("border-bottom: 1px solid #e2e8f0;")

class DashboardTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; font-family: 'Roboto'; color: #2d3748; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Metrics Section (Card-Based)
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)

        self.metrics = [
            ("Active Projects", "📋", "active_projects", 0),
            ("Total Artisans", "👥", "total_artisans", 0),
            ("Upcoming Deadlines (7 days)", "⏰", "upcoming_deadlines", 0),
            ("Artisans Available", "🟢", "artisan_availability", "0 / 0")
        ]

        for idx, (title, icon, key, value) in enumerate(self.metrics):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                    border: 1px solid #e2e8f0;
                }
                QFrame:hover {
                    background-color: #f7fafc;
                }
            """)
            card_layout = QHBoxLayout(card)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px; margin-right: 10px;")
            card_layout.addWidget(icon_label)

            text_layout = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 14px; font-family: 'Roboto'; color: #718096;")
            text_layout.addWidget(title_label)

            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-size: 20px; font-weight: bold; font-family: 'Roboto'; color: #2d3748;")
            value_label.setObjectName(f"{key}_value")
            text_layout.addWidget(value_label)

            card_layout.addLayout(text_layout)

            # Make the card clickable
            card.mousePressEvent = lambda event, k=key: self.filter_deadlines(k)
            metrics_grid.addWidget(card, 0, idx)

        layout.addLayout(metrics_grid)

        # Main Content Grid
        content_grid = QGridLayout()
        content_grid.setSpacing(20)

        # Project Status Breakdown (Donut Chart)
        chart_card = QFrame()
        chart_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
        """)
        chart_layout = QVBoxLayout(chart_card)

        chart_title = QLabel("Project Status Breakdown")
        chart_title.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Roboto'; color: #2d3748; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)

        self.status_chart = FigureCanvas(plt.Figure(figsize=(5, 3)))
        chart_layout.addWidget(self.status_chart)

        content_grid.addWidget(chart_card, 0, 0)

        # Critical Deadlines List
        deadlines_card = QFrame()
        deadlines_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
        """)
        deadlines_layout = QVBoxLayout(deadlines_card)

        deadlines_label = QLabel("Critical Deadlines (Next 7 Days)")
        deadlines_label.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Roboto'; color: #2d3748; margin-bottom: 10px;")
        deadlines_layout.addWidget(deadlines_label)

        self.deadlines_table = QTableWidget()
        self.deadlines_table.setColumnCount(3)
        self.deadlines_table.setHorizontalHeaderLabels(["Project Name", "End Date", "Assigned Artisans"])
        self.deadlines_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.deadlines_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.deadlines_table.setStyleSheet("""
            QTableWidget {
                font-family: 'Roboto';
                font-size: 14px;
                border: none;
            }
            QHeaderView::section {
                font-weight: bold;
                background-color: #f7fafc;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:hover {
                background-color: #edf2f7;
            }
        """)
        self.deadlines_table.setAlternatingRowColors(True)
        self.deadlines_table.setSortingEnabled(True)
        deadlines_layout.addWidget(self.deadlines_table)

        content_grid.addWidget(deadlines_card, 0, 1)

        # Artisan Workload Overview
        workload_card = QFrame()
        workload_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
        """)
        workload_layout = QVBoxLayout(workload_card)

        workload_label = QLabel("Artisan Workload Overview (Next 30 Days)")
        workload_label.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Roboto'; color: #2d3748; margin-bottom: 10px;")
        workload_layout.addWidget(workload_label)

        self.workload_table = QTableWidget()
        self.workload_table.setColumnCount(3)
        self.workload_table.setHorizontalHeaderLabels(["Artisan Name", "Projects Assigned", "Total Days"])
        self.workload_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.workload_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.workload_table.setStyleSheet("""
            QTableWidget {
                font-family: 'Roboto';
                font-size: 14px;
                border: none;
            }
            QHeaderView::section {
                font-weight: bold;
                background-color: #f7fafc;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:hover {
                background-color: #edf2f7;
            }
        """)
        self.workload_table.setAlternatingRowColors(True)
        self.workload_table.setSortingEnabled(True)
        workload_layout.addWidget(self.workload_table)

        content_grid.addWidget(workload_card, 1, 0)

        # Recent Activity Log (Timeline)
        activity_card = QFrame()
        activity_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
        """)
        activity_layout = QVBoxLayout(activity_card)

        activity_label = QLabel("Recent Activity")
        activity_label.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Roboto'; color: #2d3748; margin-bottom: 10px;")
        activity_layout.addWidget(activity_label)

        self.activity_scroll = QScrollArea()
        self.activity_scroll.setWidgetResizable(True)
        self.activity_widget = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_widget)
        self.activity_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.activity_scroll.setWidget(self.activity_widget)
        self.activity_scroll.setStyleSheet("border: none;")
        activity_layout.addWidget(self.activity_scroll)

        content_grid.addWidget(activity_card, 1, 1)

        layout.addLayout(content_grid)

        # Spacer to push content to the top
        layout.addStretch()

    def filter_deadlines(self, key):
        if key != "upcoming_deadlines":
            return  # Only filter when clicking "Upcoming Deadlines"
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)
        filtered_projects = []
        for project in self.all_deadline_projects:
            end_date = datetime.strptime(project[1], "%Y-%m-%d")
            if today <= end_date <= seven_days_later:
                filtered_projects.append(project)
        self.deadlines_table.setRowCount(len(filtered_projects))
        for row, (project_name, end_date, artisans) in enumerate(filtered_projects):
            self.deadlines_table.setItem(row, 0, QTableWidgetItem(project_name))
            self.deadlines_table.setItem(row, 1, QTableWidgetItem(end_date))
            self.deadlines_table.setItem(row, 2, QTableWidgetItem(artisans))
            # Color code based on urgency
            days_until_due = (datetime.strptime(end_date, "%Y-%m-%d") - today).days
            color = "#e53e3e" if days_until_due <= 2 else "#d69e2e" if days_until_due <= 5 else "#38a169"
            for col in range(3):
                item = self.deadlines_table.item(row, col)
                if item:
                    item.setBackground(QColor(color))
        self.deadlines_table.resizeColumnsToContents()

    def load_data(self):
        # Fetch active projects
        active_projects = self.db.get_projects()
        active_projects = [p for p in active_projects if p[4] == "Active"]
        self.metrics[0] = ("Active Projects", "📋", "active_projects", len(active_projects))
        self.findChild(QLabel, "active_projects_value").setText(str(len(active_projects)))

        # Fetch total artisans
        artisans = self.db.get_artisans()
        self.metrics[1] = ("Total Artisans", "👥", "total_artisans", len(artisans))
        self.findChild(QLabel, "total_artisans_value").setText(str(len(artisans)))

        # Fetch upcoming deadlines (within 7 days)
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)
        upcoming_deadlines = 0
        self.all_deadline_projects = []
        for project in active_projects:
            end_date = datetime.strptime(project[3], "%Y-%m-%d")
            # Fetch assigned artisans
            assignments = self.db.cursor.execute(
                "SELECT a.name FROM artisans a JOIN assignments ass ON a.id = ass.artisan_id WHERE ass.project_id = ?",
                (project[0],)
            ).fetchall()
            assigned_artisans = ", ".join(a[0] for a in assignments) if assignments else "None"
            self.all_deadline_projects.append((project[1], project[3], assigned_artisans))
            if today <= end_date <= seven_days_later:
                upcoming_deadlines += 1
        self.metrics[2] = ("Upcoming Deadlines (7 days)", "⏰", "upcoming_deadlines", upcoming_deadlines)
        self.findChild(QLabel, "upcoming_deadlines_value").setText(str(upcoming_deadlines))

        # Fetch artisan availability
        assignments = self.db.get_assignments()
        assigned_artisans = set(a[1] for a in assignments)  # artisan_id from assignments
        total_artisans = len(artisans)
        available_artisans = total_artisans - len(assigned_artisans)
        self.metrics[3] = ("Artisans Available", "🟢", "artisan_availability", f"{available_artisans} / {total_artisans}")
        self.findChild(QLabel, "artisan_availability_value").setText(f"{available_artisans} / {total_artisans}")

        # Project Status Breakdown (Donut Chart)
        status_counts = {"Active": 0, "Completed": 0, "On Hold": 0, "Delayed": 0}
        all_projects = self.db.get_projects()
        for project in all_projects:
            status = project[4]
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1

        self.status_chart.figure.clear()
        ax = self.status_chart.figure.add_subplot(111)
        labels = [k for k, v in status_counts.items() if v > 0]
        sizes = [v for k, v in status_counts.items() if v > 0]
        colors = ['#38a169', '#2d3748', '#e53e3e', '#d69e2e']  # Green, Dark Gray, Red, Yellow
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, 
                                          wedgeprops=dict(width=0.3))  # Donut chart with width=0.3
        ax.axis('equal')
        ax.set_title("Project Status Breakdown", fontsize=12, fontfamily='Roboto', pad=10)
        for text in texts:
            text.set_fontfamily('Roboto')
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontfamily('Roboto')
            autotext.set_fontsize(8)
        self.status_chart.draw()

        # Populate deadlines table
        self.deadlines_table.setRowCount(len(self.all_deadline_projects))
        for row, (project_name, end_date, artisans) in enumerate(self.all_deadline_projects):
            self.deadlines_table.setItem(row, 0, QTableWidgetItem(project_name))
            self.deadlines_table.setItem(row, 1, QTableWidgetItem(end_date))
            self.deadlines_table.setItem(row, 2, QTableWidgetItem(artisans))
            # Color code based on urgency
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
            days_until_due = (end_date_dt - today).days
            color = "#e53e3e" if days_until_due <= 2 else "#d69e2e" if days_until_due <= 5 else "#38a169"
            for col in range(3):
                item = self.deadlines_table.item(row, col)
                if item:
                    item.setBackground(QColor(color))
        self.deadlines_table.resizeColumnsToContents()

        # Artisan Workload Overview
        thirty_days_later = today + timedelta(days=30)
        workload_data = []
        for artisan in artisans:
            if not artisan:  # Skip if artisan is None or empty
                continue
            try:
                artisan_id = artisan[0]  # id
                artisan_name = artisan[1]  # name
            except (IndexError, TypeError) as e:
                print(f"Error processing artisan: {artisan}, {e}")
                continue
            artisan_assignments = [a for a in assignments if a[1] == artisan_id]
            projects_assigned = len(artisan_assignments)
            total_days = 0
            for assignment in artisan_assignments:
                start_date = datetime.strptime(assignment[3], "%Y-%m-%d")
                end_date = datetime.strptime(assignment[4], "%Y-%m-%d")
                start = max(start_date, today)
                end = min(end_date, thirty_days_later)
                if start <= end:
                    days = (end - start).days + 1
                    total_days += days
            workload_data.append((artisan_name, projects_assigned, total_days))

        self.workload_table.setRowCount(len(workload_data))
        for row, (artisan_name, projects_assigned, total_days) in enumerate(workload_data):
            self.workload_table.setItem(row, 0, QTableWidgetItem(artisan_name))
            self.workload_table.setItem(row, 1, QTableWidgetItem(str(projects_assigned)))
            self.workload_table.setItem(row, 2, QTableWidgetItem(str(total_days)))
            # Color code based on workload
            color = "#e53e3e" if total_days > 25 else "#d69e2e" if total_days > 15 else "#38a169"
            for col in range(3):
                item = self.workload_table.item(row, col)
                if item:
                    item.setBackground(QColor(color))
        self.workload_table.resizeColumnsToContents()

        # Recent Activity Log (Timeline)
        activities = self.db.get_recent_activities(limit=10)
        for i in reversed(range(self.activity_layout.count())):
            widget = self.activity_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for action, details, timestamp in activities:
            entry = TimelineEntry(action, details, timestamp)
            self.activity_layout.addWidget(entry)

    def refresh(self):
        """Refresh the dashboard data."""
        self.load_data()