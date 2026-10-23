# Student Management System (Python)

A desktop student record manager built with Python, Tkinter, and SQLite.

## Features
- Add student records
- View all records in a table
- Search by roll number, name, course, or email
- Update selected records
- Delete records with confirmation
- Validate required fields, age, and basic email format
- Store records persistently in a local SQLite database

## Requirements
- Python 3.9 or newer recommended
- Tkinter (usually included with Python on Windows)
- No third-party packages required

## Run the project
1. Extract the ZIP file.
2. Open a terminal in the `StudentManagementSystem` folder.
3. Run:

   ```bash
   python main.py
   ```

   On some systems, use `python3 main.py`.

4. The `students.db` database file is created automatically on first launch.

## Notes
- Roll numbers must be unique.
- Fields marked with `*` are required.
- Back up `students.db` if you need to preserve your records when moving the project.
