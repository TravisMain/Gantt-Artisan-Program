# ui/styles/stylesheet.py
STYLESHEET = """
QMainWindow { 
    background-color: #F5F5F7;  /* Soft white for main window */
}
QWidget#centralWidget {
    background-color: #F5F5F7;
}
QWidget#topBar { 
    background-color: #E8ECEF;  /* Slightly darker grey for top bar */
    border-bottom: none;
    border-bottom: 1px solid #D1D5DB;  /* Subtle border to replace box-shadow */
}
QWidget#sidebar { 
    background-color: #1C2526;  /* Dark charcoal grey for sidebar */
    border-radius: 8px;
}
QLabel { 
    font-family: 'SF Pro', 'Roboto', sans-serif;
    font-size: 14px; 
    color: #1C2526;  /* Dark charcoal for text */
}
QLabel#topBarLabel { 
    font-family: 'SF Pro', 'Roboto', sans-serif;
    font-size: 15px;  /* 10% larger than before */
    font-weight: bold;
    color: #1C2526;
}
QPushButton { 
    background-color: #007AFF;  /* Apple blue */
    color: white; 
    border-radius: 6px; 
    padding: 8px; 
    font-family: 'SF Pro', 'Roboto', sans-serif; 
    font-size: 12px; 
    border: none;
}
QPushButton:hover { 
    background-color: #005BB5;  /* Darker blue on hover */
}
QPushButton#sidebarButton { 
    color: white; 
    text-align: left; 
    background-color: transparent; 
    padding: 9.2px;
    font-family: 'SF Pro', 'Roboto', sans-serif; 
    font-size: 13.8px;
}
QPushButton#sidebarButton:hover { 
    background-color: #2E3A3B;  /* Slightly lighter grey on hover */
}
QPushButton#chatbotButton { 
    background-color: #007AFF; 
    color: white; 
    border-radius: 4px; 
    padding: 3px; 
    position: absolute; 
    bottom: 5px; 
    left: 5px; 
    width: 20px; 
    height: 20px; 
    font-size: 12px;
}
QPushButton#chatbotButton:hover { 
    background-color: #005BB5;
}
QComboBox { 
    border: 1px solid #E0E0E0; 
    border-radius: 6px; 
    padding: 5px; 
    font-family: 'SF Pro', 'Roboto', sans-serif; 
    font-size: 12px; 
    background-color: white;
}
QTreeWidget { 
    background-color: #1C2526; 
    color: white; 
    border: none; 
    font-family: 'SF Pro', 'Roboto', sans-serif; 
    font-size: 12px; 
}
QDialog { 
    background-color: #FFFFFF; 
}
QLineEdit#searchInput { 
    border: 2px solid #E0E0E0; 
    border-radius: 6px; 
    padding: 10px; 
    font-family: 'SF Pro', 'Roboto', sans-serif; 
    font-size: 14px; 
    background-color: white;
}
"""