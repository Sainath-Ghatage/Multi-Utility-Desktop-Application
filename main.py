# run_app.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QDialog,
    QPushButton, QLabel, QSplitter
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize

# Import the refactored widgets from their files
from cv_generator_widget import CVGeneratorWidget
from calculator_widget import CalculatorWidget
from todo_widget import ToDoWidget
from notes_widget import NotesWidget

# Import the master database initializer
import database_init

class StartupDialog(QDialog):
    """
    A simple dialog that asks the user which application to start with.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Multi-Utility Application")
        self.setModal(True)
        self.selection = 0  # Default to first app (CV)

        layout = QVBoxLayout(self)
        
        label = QLabel("Choose an application to start with:")
        label.setFont(QFont("Arial", 14))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.btn_cv = QPushButton("CV Generator")
        self.btn_notes = QPushButton("Notes App")
        self.btn_todo = QPushButton("To-Do List")
        self.btn_calc = QPushButton("Calculator")

        self.btn_cv.clicked.connect(lambda: self.select_app(0))
        self.btn_notes.clicked.connect(lambda: self.select_app(1))
        self.btn_todo.clicked.connect(lambda: self.select_app(2))
        self.btn_calc.clicked.connect(lambda: self.select_app(3))

        for btn in [self.btn_cv, self.btn_notes, self.btn_todo, self.btn_calc]:
            btn.setFont(QFont("Arial", 12))
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

    def select_app(self, index):
        self.selection = index
        self.accept()

class AppHubWindow(QMainWindow):
    """
    The main application window.
    Contains the sidebar for navigation and the QStackedWidget
    to display the selected application.
    """
    def __init__(self, initial_index=0):
        super().__init__()
        self.setWindowTitle("Multi-Utility Application")
        self.setGeometry(100, 100, 1000, 800)

        # Main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Sidebar (Navigation) ---
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(180) # Set a fixed width for the sidebar
        self.nav_list.addItems(["CV Generator", "Notes", "To-Do List", "Calculator"])
        self.nav_list.setFont(QFont("Arial", 12))
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                padding-top: 10px;
            }
            QListWidget::item {
                padding: 12px 15px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
                border-left: 5px solid #2980b9;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        main_layout.addWidget(self.nav_list)

        # --- Main Content Area (Stacked) ---
        self.stack = QStackedWidget()
        
        # Instantiate and add each application "page"
        self.cv_gen_widget = CVGeneratorWidget()
        self.notes_widget = NotesWidget()
        self.todo_widget = ToDoWidget()
        self.calc_widget = CalculatorWidget()

        self.stack.addWidget(self.cv_gen_widget) # Index 0
        self.stack.addWidget(self.notes_widget)  # Index 1
        self.stack.addWidget(self.todo_widget)   # Index 2
        self.stack.addWidget(self.calc_widget)   # Index 3

        main_layout.addWidget(self.stack)

        # --- Connections ---
        # Connect the sidebar list to the stacked widget
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        
        # Set the initial app
        self.nav_list.setCurrentRow(initial_index)
        self.stack.setCurrentIndex(initial_index)


if __name__ == '__main__':
    # Initialize all databases BEFORE starting the app
    database_init.initialize_all_databases()

    app = QApplication(sys.argv)
    
    # Show the startup dialog first
    startup_dialog = StartupDialog()
    
    # Only show the main window if the user made a selection
    if startup_dialog.exec():
        initial_app_index = startup_dialog.selection
        
        main_window = AppHubWindow(initial_app_index)
        main_window.show()
        sys.exit(app.exec())