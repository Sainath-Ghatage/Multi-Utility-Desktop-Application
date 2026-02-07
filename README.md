# Multi-Utility Desktop Application

A comprehensive, all-in-one desktop productivity suite built with Python and PyQt6. This application integrates four essential tools—a CV Generator, Notes Manager, To-Do List, and Calculator—into a single, unified interface backed by a local SQLite database for data persistence.

## Features

### 1. CV Generator (Resume Builder)
A powerful tool to automate resume creation.
* **Profile Management:** Create, save, update, and delete multiple user profiles.
* **PDF Export:** Generates professional-quality PDF resumes using the ReportLab library.
* **Data Fields:** Handles personal details, career objectives, skills, education history, and work experience.
* **Photo Support:** Includes image processing (using Pillow) to crop and format profile photos.

### 2. Notes Application
A dedicated space for managing personal or professional notes.
* **Search Function:** Real-time search bar to filter notes by title or content.
* **CRUD Operations:** Create, Read, Update, and Delete notes seamlessly.
* **Persistent Storage:** All notes are stored securely in a local SQLite database.

### 3. To-Do List Manager
Stay organized with a robust task tracker.
* **Task Reminders:** Set specific dates and times for tasks; the app triggers popup alerts when a task is due.
* **Status Tracking:** Checkboxes to mark tasks as completed (with visual strikethrough styling).
* **Database Integration:** Tasks persist between sessions, ensuring you never lose your list.

### 4. Calculator
A functional GUI calculator for quick arithmetic.
* **History Panel:** Displays a running log of previous calculations for easy reference.
* **Error Handling:** Gracefully handles errors (like division by zero) without crashing.
* **Keyboard Support:** Supports keyboard input for faster usage.

## Tech Stack

* **Language:** Python 3.10+
* **GUI Framework:** PyQt6 (Qt Designer & Custom QSS Styling)
* **Database:** SQLite3
* **PDF Generation:** ReportLab
* **Image Processing:** Pillow (PIL)

## Project Structure

```text
├── main.py                  # Entry point (App Hub & Navigation)
├── database_init.py         # Handles SQLite database creation and table schemas
├── cv_generator_widget.py   # CV Generator logic and PDF rendering
├── notes_widget.py          # Notes management logic
├── todo_widget.py           # To-Do list logic and reminder system
├── todo_database_funcs.py   # Database helper functions for the To-Do module
├── calculator_widget.py     # Calculator logic and history handling
└── app_data.db              # Local database (generated upon first run)  
```

## Installation & Usage
### Clone the repository:

```text
git clone https://github.com/Sainath-Ghatage/Multi-Utility-Desktop-Application.git
cd Multi-Utility-Desktop-Application
```

### Install dependencies:

```text
pip install PyQt6 reportlab Pillow
```

### Run the application:

```text
python main.py
```

## License
This project is for educational purposes. Feel free to fork and improve it!
