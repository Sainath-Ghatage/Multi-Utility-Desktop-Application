# notes_widget.py
import sys
import sqlite3
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QGridLayout, QPushButton, QLabel,
    QDialog, QTextEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

# Define the single database name
DB_NAME = 'app_data.db'

# --- Database Management ---
# init_db removed (now in database_init.py)

def get_all_notes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()
    conn.close()
    return notes

def search_notes(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("SELECT id, title, content FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC",
                   (search_term, search_term))
    notes = cursor.fetchall()
    conn.close()
    return notes

# --- Note Editor Dialog (Unchanged, as it's self-contained) ---

class NoteEditorDialog(QDialog):
    def __init__(self, note_id=None, title="", content="", parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.is_new_note = (note_id is None)

        self.setWindowTitle("Edit Note" if not self.is_new_note else "Create New Note")
        self.setMinimumSize(400, 500)

        self.layout = QVBoxLayout(self)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Note Title...")
        self.title_input.setText(title)
        self.layout.addWidget(self.title_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Start writing your note here...")
        self.content_input.setText(content)
        self.layout.addWidget(self.content_input)

        self.button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Note")
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.save_note)
        self.button_layout.addWidget(self.save_button)

        if not self.is_new_note:
            self.delete_button = QPushButton("Delete Note")
            self.delete_button.setObjectName("DeleteButton")
            self.delete_button.clicked.connect(self.delete_note)
            self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

    def save_note(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Title cannot be empty.")
            return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if self.is_new_note:
            cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        else:
            cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, self.note_id))
        conn.commit()
        conn.close()
        self.accept()

    def delete_note(self):
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this note?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (self.note_id,))
            conn.commit()
            conn.close()
            self.accept()

# --- Main Application Window (Refactored to QWidget) ---

class NotesWidget(QWidget): # Changed from QMainWindow
    def __init__(self):
        super().__init__()
        # Removed setWindowTitle and setGeometry
        
        self.setObjectName("CentralWidget") # This was the name in your original file
        main_layout = QVBoxLayout(self) # Layout applied directly to self
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search for a note...")
        self.search_bar.textChanged.connect(self.filter_notes)
        main_layout.addWidget(self.search_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("ScrollArea")
        main_layout.addWidget(self.scroll_area)

        self.notes_container = QWidget()
        self.notes_container.setObjectName("notes_container")
        self.notes_grid = QGridLayout(self.notes_container)
        self.notes_grid.setSpacing(15)
        self.notes_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.notes_container)

        self.load_notes()
        
        # Apply the stylesheet directly to this widget
        self.setStyleSheet("""
            * {
                font-family: Arial, sans-serif;
            }
            /* Target this widget specifically */
            QWidget#CentralWidget, QWidget#notes_container {
                background-color: #f7f9fc; 
            }
            QTextEdit, QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QDialog {
                background-color: #ffffff;
            }
            QScrollArea#ScrollArea { border: none; }
            QPushButton#NoteCard {
                background-color: #ffffff;
                border: 1px solid #e0e5ec;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton#NoteCard:hover {
                border-color: #87ceeb;
                background-color: #fdfdfd;
            }
            QLabel#NoteTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#NoteContent {
                font-size: 13px;
                color: #34495e;
            }
            QPushButton#AddButton {
                font-size: 50px;
                font-weight: 300;
                color: #87ceeb;
                background-color: #f0f8ff;
                border: 2px dashed #b0e0e6;
                border-radius: 8px;
            }
            QPushButton#AddButton:hover {
                background-color: #e6f7ff;
                color: #66c2e8;
            }
            QPushButton#SaveButton {
                background-color: #0275d8;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton#SaveButton:hover {
                background-color: #025aa5;
            }
            QPushButton#DeleteButton {
                background-color: #d9534f;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton#DeleteButton:hover { background-color: #c9302c; }
            QMessageBox {
                background-color: #f7f9fc;
            }
            QMessageBox QLabel {
                color: #000000;
            }
        """)

    def create_note_card(self, note_id, title, content):
        card = QPushButton()
        card.setFixedSize(200, 180)
        card.setObjectName("NoteCard")
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        card_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setObjectName("NoteTitle")
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        card_layout.addWidget(line)

        preview_text = (content[:150] + '...') if len(content) > 150 else content
        content_label = QLabel(preview_text)
        content_label.setObjectName("NoteContent")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(content_label)
        
        card_layout.addStretch()
        card.clicked.connect(partial(self.open_note_editor, note_id, title, content))
        return card

    def clear_grid(self):
        while self.notes_grid.count():
            child = self.notes_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_notes(self, notes_data=None):
        self.clear_grid()
        
        add_note_button = QPushButton("+")
        add_note_button.setObjectName("AddButton")
        add_note_button.setFixedSize(200, 180)
        add_note_button.clicked.connect(self.open_new_note_editor)
        self.notes_grid.addWidget(add_note_button, 0, 0)

        if notes_data is None: notes_data = get_all_notes() # Calls helper func

        row, col = 0, 1
        items_per_row = 4
        for note_id, title, content in notes_data:
            if col >= items_per_row:
                col = 0
                row += 1
            note_card = self.create_note_card(note_id, title, content)
            self.notes_grid.addWidget(note_card, row, col)
            col += 1

    def filter_notes(self):
        query = self.search_bar.text()
        self.load_notes(notes_data=search_notes(query)) # Calls helper func

    def open_note_editor(self, note_id, title, content):
        dialog = NoteEditorDialog(note_id, title, content, self)
        if dialog.exec(): self.filter_notes()

    def open_new_note_editor(self):
        dialog = NoteEditorDialog(parent=self)
        if dialog.exec():
            self.search_bar.clear()
            self.load_notes()

# --- Application Entry Point Removed ---