# cv_generator_widget.py
import sqlite3
import os 
import io 
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QScrollArea, QGroupBox, 
    QMessageBox, QFileDialog, QHBoxLayout, QLabel, QComboBox,
    QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

# --- PDF Generation Imports ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, black, gray
from reportlab.lib.units import inch

# --- Image Processing Import (Pillow) ---
try:
    from PIL import Image as PILImage, ImageDraw, ImageOps
except ImportError:
    print("Pillow library not found. Please install it: pip install Pillow")

# Define the single database name
DB_NAME = 'app_data.db'

# --- PDF STYLES ---
HEADING_GRAY = HexColor('#363636')
BODY_TEXT_GRAY = HexColor('#333333')
LINE_COLOR = HexColor('#cccccc')
UI_BLUE = HexColor('#4A90E2') 


class CVGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.work_experience_widgets = []
        self.education_widgets = []
        self.photo_path = None
        self.current_profile_id = None # Track the loaded profile

        self.setup_ui()
        
        # --- STYLESHEET (MODIFIED) ---
        # I have added a new block at the end for "QInputDialog"
        self.setStyleSheet("""
            /* --- General Styles --- */
            #CVWidget {
                font-family: Arial;
                font-size: 13px;
                background-color: #f4f4f4;
            }
            #CVWidget QScrollArea, #CVWidget QWidget#ScrollContent {
                background-color: #f4f4f4;
                border: none;
            }
            #CVWidget QLabel {
                color: #000000;
                background-color: transparent;
            }
            #PhotoLabel {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #ffffff;
                color: #aaaaaa;
                padding: 5px;
            }
            #CVWidget QLineEdit, #CVWidget QTextEdit, #CVWidget QComboBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
            #CVWidget QComboBox::drop-down {
                border: none;
            }
            #CVWidget QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f4f4f4;
            }
            #CVWidget QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #000000;
            }
            #CVWidget QPushButton {
                background-color: #4A90E2; 
                color: white; 
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            #CVWidget QPushButton:hover {
                background-color: #367ac9; 
            }
            #CVWidget QPushButton:pressed {
                background-color: #2a6bb5; 
            }
            #CVWidget QPushButton#DeleteButton {
                background-color: #d9534f;
            }
            #CVWidget QPushButton#DeleteButton:hover {
                background-color: #c9302c;
            }
            
            /* --- STYLES FOR QMESSAGEBOX --- */
            QMessageBox {
                background-color: #f4f4f4;
            }
            QMessageBox QLabel {
                color: #000000;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #367ac9; 
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a6bb5; 
            }
            
            /* --- NEW: STYLES FOR QINPUTDIALOG --- */
            QInputDialog {
                background-color: #f4f4f4;
                min-width: 300px;
            }
            QInputDialog QLabel {
                color: #000000; /* Black text */
                background-color: transparent;
                font-size: 13px;
            }
            QInputDialog QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
            QInputDialog QPushButton {
                background-color: #4A90E2; /* Blue button */
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }
            QInputDialog QPushButton:hover {
                background-color: #367ac9; 
            }
            QInputDialog QPushButton:pressed {
                background-color: #2a6bb5; 
            }
        """)
        self.setObjectName("CVWidget")


    def setup_ui(self):
        """Sets up the main user interface."""
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent") 
        self.scroll_area.setWidget(self.scroll_content)
        self.form_container_layout = QVBoxLayout(self.scroll_content)

        # --- NEW: Profile Management Section ---
        profile_group = QGroupBox("Manage Profiles")
        profile_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self._on_profile_selected)
        
        self.delete_profile_btn = QPushButton("Delete")
        self.delete_profile_btn.setObjectName("DeleteButton")
        self.delete_profile_btn.clicked.connect(self.delete_profile)

        profile_layout.addWidget(QLabel("Select Profile:"))
        profile_layout.addWidget(self.profile_combo, 1) # Add stretch
        profile_layout.addWidget(self.delete_profile_btn)
        
        profile_group.setLayout(profile_layout)
        self.form_container_layout.addWidget(profile_group)
        
        self._load_profile_list() # Populate the dropdown

        # --- Photo Section (Unchanged) ---
        photo_group = QGroupBox("Your Photo")
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Click 'Browse' to select a photo\n(Square preferred)")
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setObjectName("PhotoLabel")
        self.browse_photo_btn = QPushButton("Browse Photo")
        self.browse_photo_btn.clicked.connect(self.browse_photo)
        photo_layout.addWidget(self.photo_label)
        photo_layout.addWidget(self.browse_photo_btn)
        photo_layout.addStretch()
        photo_group.setLayout(photo_layout)
        self.form_container_layout.addWidget(photo_group)

        # --- Personal Details (Unchanged) ---
        personal_details_group = QGroupBox("Personal Details (Mandatory)")
        personal_details_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        self.location_input = QLineEdit()
        personal_details_layout.addRow("Full Name:", self.name_input)
        personal_details_layout.addRow("Contact Number:", self.contact_input)
        personal_details_layout.addRow("Email Address:", self.email_input)
        personal_details_layout.addRow("Location:", self.location_input)
        personal_details_group.setLayout(personal_details_layout)
        self.form_container_layout.addWidget(personal_details_group)

        # --- Career Objective (Unchanged) ---
        objective_group = QGroupBox("Career Objective (Mandatory)")
        objective_layout = QVBoxLayout()
        self.objective_input = QTextEdit()
        objective_layout.addWidget(self.objective_input)
        objective_group.setLayout(objective_layout)
        self.form_container_layout.addWidget(objective_group)

        # --- Skills (Unchanged) ---
        skills_group = QGroupBox("Skills (Mandatory)")
        skills_layout = QVBoxLayout()
        self.skills_input = QTextEdit()
        self.skills_input.setPlaceholderText("Enter skills separated by commas, bullets, or new lines...")
        skills_layout.addWidget(self.skills_input)
        skills_group.setLayout(skills_layout)
        self.form_container_layout.addWidget(skills_group)

        # --- Education Section (Unchanged) ---
        self.education_section_layout = QVBoxLayout()
        education_container = QGroupBox("Education")
        education_container.setLayout(self.education_section_layout)
        self.form_container_layout.addWidget(education_container)
        self.add_education_btn = QPushButton("Add More Education")
        self.add_education_btn.clicked.connect(self.add_education_fields)
        self.form_container_layout.addWidget(self.add_education_btn)
        self.add_education_fields() 

        # --- Work Experience (Unchanged) ---
        self.work_experience_section = QVBoxLayout()
        work_experience_container = QGroupBox("Work Experience")
        work_experience_container.setLayout(self.work_experience_section)
        self.form_container_layout.addWidget(work_experience_container)
        self.add_experience_btn = QPushButton("Add More Work Experience")
        self.add_experience_btn.clicked.connect(self.add_experience_fields)
        self.form_container_layout.addWidget(self.add_experience_btn)
        self.add_experience_fields() 

        # --- Action Buttons (MODIFIED) ---
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Current Profile")
        self.save_btn.clicked.connect(self.save_data)
        
        self.save_as_new_btn = QPushButton("Save As New Profile...")
        self.save_as_new_btn.clicked.connect(self.save_as_new)
        
        self.generate_pdf_btn = QPushButton("Generate PDF")
        self.generate_pdf_btn.clicked.connect(self.generate_pdf)
        
        # Removed the old "Load" button
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.save_as_new_btn)
        button_layout.addWidget(self.generate_pdf_btn)
        
        self.form_container_layout.addSpacing(20)
        self.form_container_layout.addLayout(button_layout)
        
    # --- NEW: Method to clear all fields ---
    def _clear_all_fields(self):
        """Resets all input fields to a blank 'New CV' state."""
        self.name_input.clear()
        self.contact_input.clear()
        self.email_input.clear()
        self.location_input.clear()
        self.objective_input.clear()
        self.skills_input.clear()
        
        self.photo_path = None
        self.load_photo_preview(None)
        
        # Clear dynamic work experience fields
        for item in self.work_experience_widgets:
            item['group'].deleteLater()
        self.work_experience_widgets.clear()
        
        # Clear dynamic education fields
        for item in self.education_widgets:
            item['group'].deleteLater()
        self.education_widgets.clear()
        
        # Add one blank field back
        self.add_education_fields()
        self.add_experience_fields()
        
        self.current_profile_id = None

    # --- NEW: Method to populate the dropdown ---
    def _load_profile_list(self):
        """Fetches all profile names from the DB and fills the combo box."""
        self.profile_combo.blockSignals(True) # Stop signal emission
        
        current_id = self.current_profile_id
        
        self.profile_combo.clear()
        self.profile_combo.addItem("--- Create New CV ---", None) # User data is 'None'
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name FROM profile ORDER BY profile_name")
        profiles = cursor.fetchall()
        conn.close()
        
        for profile_id, profile_name in profiles:
            self.profile_combo.addItem(profile_name, profile_id) # Store ID as user data
            
        # Try to re-select the one that was loaded
        if current_id:
            index = self.profile_combo.findData(current_id)
            if index != -1:
                self.profile_combo.setCurrentIndex(index)
        
        self.profile_combo.blockSignals(False) # Re-enable signals

    # --- NEW: Method to handle dropdown selection ---
    def _on_profile_selected(self, index):
        """Called when the user selects a profile from the combo box."""
        if index == -1: return # Ignore signals from .clear()
        
        profile_id = self.profile_combo.itemData(index)

        if profile_id is None:
            # User selected "--- Create New CV ---"
            if self.current_profile_id is None: return # Already on a new CV
            
            reply = QMessageBox.question(self, 'Confirm New',
                                         "This will clear any unsaved changes. Are you sure?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._clear_all_fields()
            else:
                # Revert to the previously selected item
                self.profile_combo.blockSignals(True)
                if self.current_profile_id:
                    index = self.profile_combo.findData(self.current_profile_id)
                    self.profile_combo.setCurrentIndex(index)
                self.profile_combo.blockSignals(False)
            return

        # If a valid profile is selected
        reply = QMessageBox.question(self, 'Confirm Load',
                                     "This will overwrite any unsaved changes. Are you sure you want to load this profile?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_data(profile_id)
        else:
            # Revert to the previously selected item
            self.profile_combo.blockSignals(True)
            if self.current_profile_id:
                index = self.profile_combo.findData(self.current_profile_id)
                self.profile_combo.setCurrentIndex(index)
            else:
                self.profile_combo.setCurrentIndex(0) # Back to "New"
            self.profile_combo.blockSignals(False)

    def browse_photo(self):
        """Opens a file dialog to select an image."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Photo", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.photo_path = file_name
            self.load_photo_preview(file_name)

    def load_photo_preview(self, path):
        """Loads the selected photo into the QLabel preview."""
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(
                self.photo_label.width(), 
                self.photo_label.height(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled_pixmap)
            self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.photo_label.setText("Click 'Browse' to select a photo\n(Square preferred)")
            self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.photo_path = None

    def add_experience_fields(self):
        experience_group = QGroupBox(f"Experience #{len(self.work_experience_widgets) + 1}")
        layout = QFormLayout()
        title_input, description_input, duration_input = QLineEdit(), QTextEdit(), QLineEdit()
        duration_input.setPlaceholderText("e.g., Nov 2024 - Dec 2024")
        layout.addRow("Job Title:", title_input)
        layout.addRow("Description:", description_input)
        layout.addRow("Duration (Optional):", duration_input)
        experience_group.setLayout(layout)
        self.work_experience_section.addWidget(experience_group)
        self.work_experience_widgets.append({
            'group': experience_group, 'title': title_input,
            'description': description_input, 'duration': duration_input
        })

    def add_education_fields(self):
        education_group = QGroupBox(f"Education #{len(self.education_widgets) + 1}")
        layout = QFormLayout()
        course_input, year_input, grade_input, institution_input = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        year_input.setPlaceholderText("e.g., 2023-2027")
        layout.addRow("Course Name:", course_input)
        layout.addRow("Year(s):", year_input)
        layout.addRow("Percentage/CGPA:", grade_input)
        layout.addRow("Institution Name:", institution_input)
        education_group.setLayout(layout)
        self.education_section_layout.addWidget(education_group)
        self.education_widgets.append({
            'group': education_group, 'course': course_input, 'year': year_input,
            'grade': grade_input, 'institution': institution_input
        })

    def validate_inputs(self, check_photo=False):
        """Checks if all mandatory fields are filled."""
        mandatory_fields = {
            "Full Name": self.name_input.text(),
            "Contact Number": self.contact_input.text(),
            "Email Address": self.email_input.text(),
            "Location": self.location_input.text(),
            "Career Objective": self.objective_input.toPlainText(),
            "Skills": self.skills_input.toPlainText()
        }
        
        missing = [name for name, value in mandatory_fields.items() if not value.strip()]
        
        # Photo is not mandatory to save, but is for PDF generation
        if check_photo and not self.photo_path:
            missing.append("Photo")
            
        if missing:
            QMessageBox.warning(
                self, "Missing Information",
                f"The following mandatory fields are missing:\n\n- " + "\n- ".join(missing)
            )
            return False
        return True

    # --- NEW: Method to save data as a new profile ---
    def save_as_new(self):
        """Saves the current form data as a new entry in the database."""
        if not self.validate_inputs(check_photo=False):
            return

        profile_name, ok = QInputDialog.getText(self, "Save As New", "Enter a name for this new profile:")
        
        if not (ok and profile_name and profile_name.strip()):
            return # User cancelled or entered blank name
            
        profile_name = profile_name.strip()
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if name already exists
        cursor.execute("SELECT id FROM profile WHERE profile_name = ?", (profile_name,))
        if cursor.fetchone():
            QMessageBox.warning(self, "Error", "A profile with this name already exists. Please choose a different name.")
            conn.close()
            return

        try:
            # Insert new profile
            cursor.execute(
                'INSERT INTO profile (profile_name, name, contact_number, email, location, objective, skills, photo_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (profile_name, self.name_input.text(), self.contact_input.text(), self.email_input.text(),
                 self.location_input.text(), self.objective_input.toPlainText(), 
                 self.skills_input.toPlainText(), self.photo_path)
            )
            new_profile_id = cursor.lastrowid
            
            # Save work experience
            for exp in self.work_experience_widgets:
                if exp['title'].text():
                    cursor.execute(
                        'INSERT INTO work_experience (profile_id, title, description, duration) VALUES (?, ?, ?, ?)',
                        (new_profile_id, exp['title'].text(), exp['description'].toPlainText(), exp['duration'].text())
                    )
            # Save education
            for edu in self.education_widgets:
                if edu['course'].text() or edu['institution'].text():
                    cursor.execute(
                        'INSERT INTO education (profile_id, course_name, year_completion, grade, institution_name) VALUES (?, ?, ?, ?, ?)',
                        (new_profile_id, edu['course'].text(), edu['year'].text(), edu['grade'].text(), edu['institution'].text())
                    )
            
            conn.commit()
            self.current_profile_id = new_profile_id
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save profile: {e}")
            conn.rollback()
        finally:
            conn.close()
            
        self._load_profile_list() # Refresh dropdown
        # Find and select the newly saved item
        index = self.profile_combo.findData(new_profile_id)
        if index != -1:
            self.profile_combo.setCurrentIndex(index)


    # --- MODIFIED: save_data now saves/updates the current profile ---
    def save_data(self):
        """Saves changes to the currently loaded profile."""
        if not self.validate_inputs(check_photo=False):
            return

        if self.current_profile_id is None:
            # This is a new, unsaved CV. Force "Save As"
            self.save_as_new()
            return
            
        # If we have a current_profile_id, UPDATE it
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE profile SET name=?, contact_number=?, email=?, location=?, objective=?, skills=?, photo_path=? WHERE id=?',
                (self.name_input.text(), self.contact_input.text(), self.email_input.text(),
                 self.location_input.text(), self.objective_input.toPlainText(), 
                 self.skills_input.toPlainText(), self.photo_path, self.current_profile_id)
            )
            
            # Nuke and pave: Delete old entries and insert current ones
            cursor.execute("DELETE FROM work_experience WHERE profile_id=?", (self.current_profile_id,))
            for exp in self.work_experience_widgets:
                if exp['title'].text():
                    cursor.execute(
                        'INSERT INTO work_experience (profile_id, title, description, duration) VALUES (?, ?, ?, ?)',
                        (self.current_profile_id, exp['title'].text(), exp['description'].toPlainText(), exp['duration'].text())
                    )
                    
            cursor.execute("DELETE FROM education WHERE profile_id=?", (self.current_profile_id,))
            for edu in self.education_widgets:
                if edu['course'].text() or edu['institution'].text():
                    cursor.execute(
                        'INSERT INTO education (profile_id, course_name, year_completion, grade, institution_name) VALUES (?, ?, ?, ?, ?)',
                        (self.current_profile_id, edu['course'].text(), edu['year'].text(), edu['grade'].text(), edu['institution'].text())
                    )
            
            conn.commit()
            QMessageBox.information(self, "Success", "Your changes have been saved successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update profile: {e}")
            conn.rollback()
        finally:
            conn.close()

    # --- MODIFIED: load_data now loads a specific profile ID ---
    def load_data(self, profile_id):
        """Loads all data for a specific profile_id into the form."""
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Clear all fields first
        self._clear_all_fields()

        # Load profile
        cursor.execute("SELECT name, contact_number, email, location, objective, skills, photo_path FROM profile WHERE id=?", (profile_id,))
        profile = cursor.fetchone()
        if profile:
            self.name_input.setText(profile[0])
            self.contact_input.setText(profile[1])
            self.email_input.setText(profile[2])
            self.location_input.setText(profile[3])
            self.objective_input.setPlainText(profile[4])
            self.skills_input.setPlainText(profile[5])
            self.photo_path = profile[6]
            self.load_photo_preview(self.photo_path) 

        # Load work experience
        cursor.execute("SELECT title, description, duration FROM work_experience WHERE profile_id=?", (profile_id,))
        experiences = cursor.fetchall()
        for item in self.work_experience_widgets: item['group'].deleteLater()
        self.work_experience_widgets.clear()
        if not experiences: self.add_experience_fields()
        else:
            for exp in experiences:
                self.add_experience_fields()
                last_exp_widget = self.work_experience_widgets[-1]
                last_exp_widget['title'].setText(exp[0])
                last_exp_widget['description'].setPlainText(exp[1])
                last_exp_widget['duration'].setText(exp[2])

        # Load education
        cursor.execute("SELECT course_name, year_completion, grade, institution_name FROM education WHERE profile_id=?", (profile_id,))
        educations = cursor.fetchall()
        for item in self.education_widgets: item['group'].deleteLater()
        self.education_widgets.clear()
        if not educations: self.add_education_fields()
        else:
            for edu in educations:
                self.add_education_fields()
                last_edu_widget = self.education_widgets[-1]
                last_edu_widget['course'].setText(edu[0])
                last_edu_widget['year'].setText(edu[1])
                last_edu_widget['grade'].setText(edu[2])
                last_edu_widget['institution'].setText(edu[3])
        
        conn.close()
        self.current_profile_id = profile_id
        # QMessageBox.information(self, "Success", "Profile loaded successfully!")

    # --- NEW: Method to delete the current profile ---
    def delete_profile(self):
        """Deletes the currently selected profile from the database."""
        if self.current_profile_id is None:
            QMessageBox.warning(self, "Error", "No profile is currently loaded to be deleted.")
            return

        profile_name = self.profile_combo.currentText()
        reply = QMessageBox.question(self, 'Confirm Delete',
                                     f"Are you sure you want to permanently delete the profile '{profile_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
            
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # The "ON DELETE CASCADE" in the database schema should handle
            # deleting work_experience and education, but we can also be explicit
            cursor.execute("DELETE FROM work_experience WHERE profile_id=?", (self.current_profile_id,))
            cursor.execute("DELETE FROM education WHERE profile_id=?", (self.current_profile_id,))
            cursor.execute("DELETE FROM profile WHERE id=?", (self.current_profile_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' has been deleted.")
            
            self._clear_all_fields()
            self._load_profile_list() # Refresh the dropdown
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to delete profile: {e}")

    # --- (Unchanged) Method for creating circular image ---
    def _create_rounded_image(self, image_path, size):
        """Helper to create a circular image using Pillow."""
        try:
            img = PILImage.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, size, PILImage.Resampling.LANCZOS)
            mask = PILImage.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img.putalpha(mask)
            temp_file = io.BytesIO()
            img.save(temp_file, format='PNG')
            temp_file.seek(0)
            return temp_file
        except Exception:
            return image_path 

    # --- (Unchanged) Method for PDF Generation ---
    def generate_pdf(self):
        # 1. VALIDATION
        if not self.validate_inputs(check_photo=True):
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CV", f"{self.name_input.text().replace(' ', '_')}_CV.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return
            
        doc = SimpleDocTemplate(file_path, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []

        # 2. DEFINE STYLES
        styles.add(ParagraphStyle(name='NameStyle', fontName='Helvetica-Bold', fontSize=28, alignment=TA_LEFT, textColor=UI_BLUE, leading=34))
        styles.add(ParagraphStyle(name='ContactStyle', fontName='Helvetica', fontSize=10, alignment=TA_LEFT, textColor=BODY_TEXT_GRAY, leading=12))
        styles.add(ParagraphStyle(name='HeadingStyle', fontName='Helvetica-Bold', fontSize=11, spaceBefore=12, spaceAfter=2, textColor=HEADING_GRAY))
        styles.add(ParagraphStyle(name='BodyStyle', fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT, textColor=BODY_TEXT_GRAY))
        styles.add(ParagraphStyle(name='ItalicBodyStyle', parent=styles['BodyStyle'], fontName='Helvetica-Oblique'))
        styles.add(ParagraphStyle(name='JobTitleStyle', fontName='Helvetica-Bold', fontSize=10, textColor=BODY_TEXT_GRAY))
        styles.add(ParagraphStyle(name='InstitutionStyle', fontName='Helvetica', fontSize=10, textColor=BODY_TEXT_GRAY))
        styles.add(ParagraphStyle(name='DateStyle', fontName='Helvetica', fontSize=10, textColor=BODY_TEXT_GRAY, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='BulletStyle', fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT, textColor=BODY_TEXT_GRAY, leftIndent=15))

        # 3. PREPARE TOP SECTION
        rounded_image_file = self._create_rounded_image(
            self.photo_path, 
            size=(int(1.25*inch), int(1.25*inch))
        )
        img_flowable = Image(rounded_image_file, width=1.25*inch, height=1.25*inch)
        img_flowable.hAlign = 'LEFT'
        
        name_para = Paragraph(self.name_input.text(), styles['NameStyle'])
        contact_info = " • ".join(filter(None, [self.email_input.text(), self.contact_input.text(), self.location_input.text()]))
        contact_para = Paragraph(contact_info, styles['ContactStyle'])
        
        # Nested Table with 3 Rows
        details_table_data = [
            [name_para],           # Row 1: Name
            [Spacer(1, 4)],        # Row 2: A 4-point vertical spacer
            [contact_para]         # Row 3: Contact
        ]
        details_table = Table(details_table_data, colWidths=[6*inch])
        details_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        # Main Top Table
        top_table_data = [
            [img_flowable, details_table] 
        ]
        top_table = Table(top_table_data, colWidths=[1.5*inch, 6*inch])
        top_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(top_table)
        story.append(Spacer(1, 0.25*inch))
        
        # 4. CAREER OBJECTIVE
        objective = self.objective_input.toPlainText()
        if objective:
            story.append(Paragraph("CAREER OBJECTIVE", styles['HeadingStyle']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6))
            story.append(Paragraph(objective, styles['ItalicBodyStyle']))

        # 5. SKILLS
        skills = self.skills_input.toPlainText()
        if skills:
            story.append(Paragraph("SKILLS", styles['HeadingStyle']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6))
            skill_items = [f"• {s.strip()}" for s in skills.replace(',', '\n').split('\n') if s.strip()]
            if not skill_items:
                pass 
            elif len(skill_items) > 6:
                num_cols = 3 if len(skill_items) > 14 else 2
                num_rows = -(-len(skill_items) // num_cols) 
                table_data = [[] for _ in range(num_rows)]
                for i, item in enumerate(skill_items):
                    row_index = i % num_rows
                    table_data[row_index].append(Paragraph(item, styles['BodyStyle']))
                for row in table_data:
                    while len(row) < num_cols:
                        row.append("")
                skill_table = Table(table_data, colWidths=[(doc.width / num_cols)] * num_cols)
                skill_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(skill_table)
            else:
                skill_list = "<br/>".join(skill_items)
                story.append(Paragraph(skill_list, styles['BodyStyle']))

        # 6. EDUCATION
        if any(edu['course'].text() or edu['institution'].text() for edu in self.education_widgets):
            story.append(Paragraph("EDUCATION", styles['HeadingStyle']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6))
            for edu in self.education_widgets:
                if edu['course'].text() or edu['institution'].text():
                    left_cell_content = []
                    p_course = Paragraph(f"<b>{edu['course'].text()}</b>", styles['BodyStyle'])
                    left_cell_content.append(p_course)
                    if edu['institution'].text():
                        p_institution = Paragraph(edu['institution'].text(), styles['InstitutionStyle'])
                        left_cell_content.append(p_institution)
                    if edu['grade'].text():
                        p_grade = Paragraph(edu['grade'].text(), styles['InstitutionStyle'])
                        left_cell_content.append(p_grade)
                    p_year = Paragraph(edu['year'].text(), styles['DateStyle'])
                    edu_table_data = [[left_cell_content, p_year]]
                    edu_table = Table(edu_table_data, colWidths=['*', 2*inch])
                    edu_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(edu_table)
                    story.append(Spacer(1, 10))

        # 7. WORK EXPERIENCE
        if any(exp['title'].text() for exp in self.work_experience_widgets):
            story.append(Paragraph("WORK EXPERIENCE", styles['HeadingStyle']))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6))
            for exp in self.work_experience_widgets:
                if exp['title'].text():
                    p_title = Paragraph(exp['title'].text(), styles['JobTitleStyle'])
                    p_duration = Paragraph(exp['duration'].text(), styles['DateStyle'])
                    row1 = Table([[p_title, p_duration]], colWidths=['*', 2*inch])
                    row1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
                    story.append(row1)
                    desc_text = exp['description'].toPlainText().replace('\n', '<br/>• ')
                    if not desc_text.startswith('• ') and desc_text:
                        desc_text = '• ' + desc_text
                    story.append(Paragraph(desc_text, styles['BulletStyle']))
                    story.append(Spacer(1, 12))
        
        # 9. BUILD THE PDF
        try:
            doc.build(story)
            QMessageBox.information(self, "Success", f"CV successfully generated at:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the PDF: {e}")
        finally:
            if isinstance(rounded_image_file, io.BytesIO):
                rounded_image_file.close()