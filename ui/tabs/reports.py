# ui/tabs/reports.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReportsTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reports Tab - Under Construction"))
