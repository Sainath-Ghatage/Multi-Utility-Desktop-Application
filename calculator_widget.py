# calculator_widget.py
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QLineEdit, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QSplitter, QListWidget, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import re # For simple validation

class CalculatorWidget(QWidget):
    """
    A simple calculator application built with PyQt6.
    (Refactored to a light theme with history and expression evaluation)
    """
    
    OPERATOR_STYLE = """
        background-color: #FF8C00; 
        color: white; 
        border-radius: 8px; 
        padding: 10px;
        border: 1px solid #e67e00;
    """

    def __init__(self):
        super().__init__()
        self.init_state()
        self.init_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def init_state(self):
        """Initializes the calculator's state."""
        self.expression = ""
        self.just_calculated = False

    def init_ui(self):
        """Sets up the user interface, layout, and widgets."""
        self.setMinimumSize(400, 500) 

        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- Left Panel: Calculator ---
        calc_widget = QWidget()
        calc_layout = QGridLayout(calc_widget)
        calc_layout.setSpacing(10)

        self.history_display = QLabel()
        self.history_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.history_display.setFont(QFont("Inter", 14))
        self.history_display.setStyleSheet("color: #555;")
        self.history_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        calc_layout.addWidget(self.history_display, 0, 0, 1, 4)

        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Inter", 36))
        self.display.setMinimumHeight(70)
        self.display.setStyleSheet("""
            background-color: #f0f0f0;
            color: black;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
        """)
        self.display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        calc_layout.addWidget(self.display, 1, 0, 1, 4)

        buttons = {
            'C': (2, 0, 1, 1), '(': (2, 1, 1, 1), ')': (2, 2, 1, 1), '%': (2, 3, 1, 1),
            '7': (3, 0, 1, 1), '8': (3, 1, 1, 1), '9': (3, 2, 1, 1), '/': (3, 3, 1, 1),
            '4': (4, 0, 1, 1), '5': (4, 1, 1, 1), '6': (4, 2, 1, 1), '*': (4, 3, 1, 1),
            '1': (5, 0, 1, 1), '2': (5, 1, 1, 1), '3': (5, 2, 1, 1), '-': (5, 3, 1, 1),
            '0': (6, 0, 1, 1), '.': (6, 1, 1, 1), 'Del': (6, 2, 1, 1), '+': (6, 3, 1, 1),
            '=': (7, 0, 1, 4)
        }
        
        for text, pos in buttons.items():
            button = QPushButton(text)
            button.setFont(QFont("Inter", 16))
            button.clicked.connect(self.on_button_click)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            calc_layout.addWidget(button, *pos)

            if text in "0123456789.":
                button.setStyleSheet("""
                    background-color: #fdfdfd; color: black; 
                    border-radius: 8px; padding: 10px; border: 1px solid #ccc;
                """)
            elif text in "+-*/%=":
                button.setStyleSheet(self.OPERATOR_STYLE)
            else: 
                button.setStyleSheet("""
                    background-color: #ddd; color: black; 
                    border-radius: 8px; padding: 10px; border: 1px solid #bbb;
                """)
        
        splitter.addWidget(calc_widget)

        # --- Right Panel: History ---
        history_widget = QWidget()
        history_widget.setObjectName("HistoryWidget")
        history_layout = QVBoxLayout(history_widget)
        
        history_label = QLabel("History")
        history_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        history_label.setStyleSheet("color: #333; margin-bottom: 5px;")
        
        self.history_list_widget = QListWidget()
        
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_list_widget)

        splitter.addWidget(history_widget)
        splitter.setSizes([700, 300]) 

        # --- STYLESHEET UPDATED ---
        # Changed background colors for #HistoryWidget and QListWidget
        self.setStyleSheet("""
            CalculatorWidget { 
                background-color: #ffffff; 
            }
            #HistoryWidget {
                background-color: #e0e0e0; /* Darker gray background */
                border-left: 1px solid #c0c0c0; /* Slightly darker border */
            }
            QListWidget {
                border: none;
                background-color: #e0e0e0; /* Match history panel background */
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
                color: #222222; /* Darker text for better contrast */
            }
        """)

    # --- All logic methods remain the same ---

    def on_button_click(self):
        button_text = self.sender().text()
        
        if button_text == "C":
            self.handle_clear()
        elif button_text == "Del":
            self.handle_delete()
        elif button_text == "=":
            self.handle_equals()
        else:
            self.append_to_expression(button_text)

    def append_to_expression(self, text):
        if self.just_calculated and text in "0123456789.(":
            self.expression = text
        elif self.just_calculated and text in "+-*/%":
            self.expression += text
        elif self.expression == "0" and text not in ".+-*/%":
            self.expression = text
        else:
            self.expression += text
            
        self.just_calculated = False
        self.update_display()

    def handle_clear(self):
        self.expression = ""
        self.history_display.clear()
        self.just_calculated = False
        self.update_display()

    def handle_delete(self):
        if self.just_calculated:
            self.expression = ""
        else:
            self.expression = self.expression[:-1]
        self.just_calculated = False
        self.update_display()

    def handle_equals(self):
        if not self.expression:
            return

        try:
            safe_expr = self.expression.replace("%", "*0.01")
            
            allowed_chars = "0123456789+-*/.() "
            if any(c not in allowed_chars for c in safe_expr):
                raise ValueError("Invalid characters")

            result = eval(safe_expr)
            
            if result == int(result):
                result_str = str(int(result))
            else:
                result_str = str(round(result, 8))

            history_entry = f"{self.expression} = {result_str}"
            self.history_list_widget.addItem(history_entry)
            self.history_list_widget.scrollToBottom()

            self.history_display.setText(self.expression + " =")
            self.expression = result_str
            self.update_display(result_str)
            self.just_calculated = True

        except Exception as e:
            self.display.setText("Error")
            self.expression = ""
            self.just_calculated = False
            print(f"Evaluation Error: {e}")

    def update_display(self, text=None):
        if text is not None:
            self.display.setText(text)
        else:
            self.display.setText(self.expression if self.expression else "0")

    # --- THIS FUNCTION HANDLES KEYBOARD INPUT ---
    # It was included in the previous update.
    def keyPressEvent(self, event):
        """Handles keyboard input."""
        key = event.key()
        text = event.text()

        if text in "0123456789.()+-*/%":
            self.append_to_expression(text)
        elif key in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Equal):
            self.handle_equals()
        elif key == Qt.Key.Key_Backspace:
            self.handle_delete()
        elif key == Qt.Key.Key_Escape:
            self.handle_clear()