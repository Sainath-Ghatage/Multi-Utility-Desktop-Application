# todo_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QLabel, QMessageBox, QDateEdit, QComboBox  # --- IMPORT UPDATED ---
)
from PyQt6.QtCore import Qt, QDate, QTimer, QDateTime  # --- IMPORT UPDATED ---
from PyQt6.QtGui import QFont, QIcon
import todo_database_funcs 

class ToDoWidget(QWidget): 
    def __init__(self):
        super().__init__()
        
        # --- STYLESHEET UPDATED ---
        # Replaced QTimeEdit with QComboBox in the rule
        # Added a new rule for QComboBox QAbstractItemView
        self.setStyleSheet("""
            ToDoWidget {
                background-color: #f0f0f0;
            }
            ToDoWidget QLabel, ToDoWidget QCheckBox {
                color: #000000;
                font-size: 14px;
            }
            /* --- RULE UPDATED --- */
            ToDoWidget QLineEdit, ToDoWidget QTextEdit, ToDoWidget QDateEdit, ToDoWidget QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            
            /* --- RULE ADDED --- */
            /* Styles the dropdown menu itself */
            ToDoWidget QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #0078d7;
            }
            
            ToDoWidget QListWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            
            ToDoWidget QListWidget::item:selected {
                background-color: #cce5ff;
                color: #000000;
            }
            
            ToDoWidget QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            ToDoWidget QPushButton:hover {
                background-color: #005a9e;
            }
            
            ToDoWidget QPushButton#DeleteButton {
                background-color: #e74c3c;
            }
            ToDoWidget QPushButton#DeleteButton:hover {
                background-color: #c0392b;
            }
            
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QMessageBox QPushButton {
               background-color: #0078d7;
               color: white;
               padding: 8px;
               min-width: 70px;
               border-radius: 5px;
            }
            
            ToDoWidget QLabel#ReminderLabel {
                color: #ecf0f1;
            }
        """)
        self.setObjectName("ToDoWidget")

        self.layout = QVBoxLayout(self)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Task Title...")
        self.layout.addWidget(self.title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter Task Description...")
        self.desc_input.setMaximumHeight(100)
        self.layout.addWidget(self.desc_input)
        
        reminder_layout = QHBoxLayout()
        
        date_label = QLabel("Reminder Date:")
        date_label.setObjectName("ReminderLabel")
        reminder_layout.addWidget(date_label)
        
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        reminder_layout.addWidget(self.date_input)
        
        reminder_layout.addSpacing(20)
        
        time_label = QLabel("Reminder Time:")
        time_label.setObjectName("ReminderLabel")
        reminder_layout.addWidget(time_label)
        
        # --- CODE UPDATED ---
        # Replaced QTimeEdit with QComboBox
        self.time_input = QComboBox()
        self.time_input.addItems(self.generate_time_list())
        self.time_input.setEditable(True)
        reminder_layout.addWidget(self.time_input)
        
        self.layout.addLayout(reminder_layout)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit Task")
        self.delete_button = QPushButton("Delete Task")
        
        self.delete_button.setObjectName("DeleteButton")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        self.layout.addLayout(button_layout)
        
        self.task_list_widget = QListWidget()
        self.layout.addWidget(self.task_list_widget)
        
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.task_list_widget.itemClicked.connect(self.populate_fields)
        
        self.triggered_reminders_this_session = set()

        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(10000)

        self.load_tasks()

    # --- NEW METHOD ADDED ---
    def generate_time_list(self):
        """Generates a list of times in 30-min intervals."""
        times = ["--:--"] # "None" option
        for h in range(24):
            times.append(f"{h:02d}:00")
            times.append(f"{h:02d}:30")
        return times

    def check_reminders(self):
        tasks = todo_database_funcs.get_all_tasks() 
        current_dt = QDateTime.currentDateTime()

        for task in tasks:
            task_id, title, _, done, reminder_date, reminder_time = task
            
            # This logic remains valid, as a "None" time will fail this check
            if done or not reminder_date or not reminder_time:
                continue
            if task_id in self.triggered_reminders_this_session:
                continue

            reminder_dt_str = f"{reminder_date} {reminder_time}"
            reminder_dt = QDateTime.fromString(reminder_dt_str, "yyyy-MM-dd HH:mm")

            if current_dt >= reminder_dt:
                QMessageBox.information(self, "🔔 Task Reminder", f"Your task is due!\n\nTask: {title}")
                self.triggered_reminders_this_session.add(task_id)

    def load_tasks(self):
        self.task_list_widget.clear()
        tasks = todo_database_funcs.get_all_tasks()
        
        for task in tasks:
            task_id, title, description, done, reminder_date, reminder_time = task
            
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 5, 5, 5)
            item_layout.setSpacing(3) 

            top_layout = QHBoxLayout()
            checkbox = QCheckBox()
            checkbox.setChecked(bool(done))
            checkbox.stateChanged.connect(lambda state, t_id=task_id: self.toggle_task_status(state, t_id))

            title_label = QLabel(title)
            title_font = QFont()
            title_font.setStrikeOut(bool(done))
            title_font.setBold(True)
            title_font.setPointSize(14)
            title_label.setFont(title_font)

            top_layout.addWidget(checkbox)
            top_layout.addWidget(title_label)
            top_layout.addStretch()
            
            if reminder_date and reminder_time:
                reminder_str = f"Due: {reminder_date} {reminder_time}"
                reminder_label = QLabel(reminder_str)
                reminder_font = QFont()
                reminder_font.setStrikeOut(bool(done))
                reminder_font.setPointSize(10)
                reminder_label.setFont(reminder_font)
                reminder_label.setStyleSheet("color: #666666; margin-left: 10px;")
                top_layout.addWidget(reminder_label)
            
            item_layout.addLayout(top_layout) 

            if description:
                first_line = description.split('\n')[0]
                
                if len(first_line) > 80:
                    desc_preview = first_line[:80] + '...'
                elif len(description) > len(first_line): 
                    desc_preview = first_line + '...'
                else: 
                    desc_preview = first_line

                desc_label = QLabel(desc_preview)
                desc_font = QFont()
                desc_font.setItalic(True)
                desc_font.setStrikeOut(bool(done))
                desc_label.setFont(desc_font)
                desc_label.setStyleSheet("color: #555555; padding-left: 28px;") 
                
                item_layout.addWidget(desc_label)

            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, task_id)
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.task_list_widget.addItem(list_item)
            self.task_list_widget.setItemWidget(list_item, item_widget)

    # --- METHOD UPDATED ---
    def add_task(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        reminder_date = self.date_input.date().toString("yyyy-MM-dd")
        
        # Get time from QComboBox
        reminder_time = self.time_input.currentText()
        if reminder_time == "--:--":
            reminder_time = None # Store as None in DB if no time is selected

        if not title:
            QMessageBox.warning(self, "Input Error", "Task title cannot be empty.")
            return

        todo_database_funcs.add_task(title, description, reminder_date, reminder_time) 
        self.clear_fields()
        self.load_tasks()

    # --- METHOD UPDATED ---
    def edit_task(self):
        selected_item = self.task_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a task to edit.")
            return

        task_id = selected_item.data(Qt.ItemDataRole.UserRole)
        new_title = self.title_input.text().strip()
        new_description = self.desc_input.toPlainText().strip()
        new_date = self.date_input.date().toString("yyyy-MM-dd")
        
        # Get time from QComboBox
        new_time = self.time_input.currentText()
        if new_time == "--:--":
            new_time = None # Store as None in DB if no time is selected

        if not new_title:
            QMessageBox.warning(self, "Input Error", "Task title cannot be empty.")
            return
        
        todo_database_funcs.update_task(task_id, new_title, new_description, new_date, new_time)
        
        self.triggered_reminders_this_session.discard(task_id)
        
        self.clear_fields()
        self.load_tasks()

    def delete_task(self):
        selected_item = self.task_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a task to delete.")
            return
            
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this task?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            todo_database_funcs.delete_task(task_id)
            self.triggered_reminders_this_session.discard(task_id)
            self.clear_fields()
            self.load_tasks()

    # --- METHOD UPDATED ---
    def populate_fields(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        tasks = todo_database_funcs.get_all_tasks() 
        task_data = next((t for t in tasks if t[0] == task_id), None)

        if task_data:
            _, title, description, _, reminder_date, reminder_time = task_data
            self.title_input.setText(title)
            self.desc_input.setPlainText(description)
            
            if reminder_date:
                self.date_input.setDate(QDate.fromString(reminder_date, "yyyy-MM-dd"))
            else:
                self.date_input.setDate(QDate.currentDate())
                
            # Set QComboBox
            if reminder_time:
                # Check if the exact time is in the dropdown
                index = self.time_input.findText(reminder_time)
                if index != -1:
                    self.time_input.setCurrentText(reminder_time)
                else:
                    # If time was custom (e.g., "14:15"), just set to "None"
                    self.time_input.setCurrentText("--:--") 
            else:
                self.time_input.setCurrentIndex(0) # Set to "--:--"

    def toggle_task_status(self, state, task_id):
        done = 1 if state == Qt.CheckState.Checked.value else 0
        todo_database_funcs.update_task_status(task_id, done)
        self.load_tasks()

    # --- METHOD UPDATED ---
    def clear_fields(self):
        self.title_input.clear()
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setCurrentText("--:--") # Set dropdown to "--:--"