# ui/tabs/artisans.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ArtisansTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Artisans Tab - Under Construction"))
