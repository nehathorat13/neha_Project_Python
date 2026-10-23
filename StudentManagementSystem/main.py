import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "students.db"


class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1100x680")
        self.root.minsize(950, 600)

        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

        self.selected_student_id = None
        self.search_var = tk.StringVar()
        self.vars = {
            "roll_no": tk.StringVar(),
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(value="Prefer not to say"),
            "course": tk.StringVar(),
            "email": tk.StringVar(),
            "phone": tk.StringVar(),
        }

        self.build_ui()
        self.load_students()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
                    gender TEXT NOT NULL,
                    course TEXT NOT NULL,
                    email TEXT,
                    phone TEXT
                )
            """)

    def build_ui(self):
        header = ttk.Frame(self.root, padding=(18, 15))
        header.pack(fill="x")
        ttk.Label(header, text="Student Management System",
                  font=("Segoe UI", 21, "bold")).pack(anchor="w")
        ttk.Label(header, text="Add, view, search, update and delete student records",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        body = ttk.Frame(self.root, padding=(18, 0, 18, 18))
        body.pack(fill="both", expand=True)

        form = ttk.LabelFrame(body, text="Student Details", padding=14)
        form.pack(side="left", fill="y", padx=(0, 14))

        fields = [
            ("Roll Number *", "roll_no"),
            ("Full Name *", "name"),
            ("Age *", "age"),
            ("Gender *", "gender"),
            ("Course *", "course"),
            ("Email", "email"),
            ("Phone", "phone"),
        ]

        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=6)
            if key == "gender":
                widget = ttk.Combobox(
                    form, textvariable=self.vars[key], state="readonly", width=25,
                    values=("Male", "Female", "Non-binary", "Prefer not to say")
                )
            else:
                widget = ttk.Entry(form, textvariable=self.vars[key], width=28)
            widget.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=6)

        button_frame = ttk.Frame(form)
        button_frame.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(16, 4))
        for col in range(2):
            button_frame.columnconfigure(col, weight=1)

        ttk.Button(button_frame, text="Add Student", command=self.add_student).grid(
            row=0, column=0, sticky="ew", padx=(0, 5), pady=4)
        ttk.Button(button_frame, text="Update Selected", command=self.update_student).grid(
            row=0, column=1, sticky="ew", padx=(5, 0), pady=4)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_student).grid(
            row=1, column=0, sticky="ew", padx=(0, 5), pady=4)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(
            row=1, column=1, sticky="ew", padx=(5, 0), pady=4)

        records = ttk.LabelFrame(body, text="Student Records", padding=10)
        records.pack(side="left", fill="both", expand=True)

        search_frame = ttk.Frame(records)
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_frame, text="Search:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=8)
        search_entry.bind("<KeyRelease>", lambda _event: self.load_students())
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).pack(side="left")

        columns = ("id", "roll_no", "name", "age", "gender", "course", "email", "phone")
        self.tree = ttk.Treeview(records, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID", "roll_no": "Roll No.", "name": "Full Name", "age": "Age",
            "gender": "Gender", "course": "Course", "email": "Email", "phone": "Phone"
        }
        widths = {
            "id": 45, "roll_no": 85, "name": 145, "age": 50, "gender": 105,
            "course": 110, "email": 170, "phone": 105
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], minwidth=40, anchor="w")

        y_scroll = ttk.Scrollbar(records, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(records, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.pack(fill="both", expand=True, side="top")
        x_scroll.pack(fill="x", side="bottom")
        y_scroll.place(relx=1.0, rely=0.16, relheight=0.78, anchor="ne")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(18, 7)).pack(fill="x")

    def get_form_data(self):
        data = {key: value.get().strip() for key, value in self.vars.items()}
        required = ("roll_no", "name", "age", "gender", "course")
        if any(not data[key] for key in required):
            messagebox.showwarning("Missing Information", "Please fill in all required fields marked with *.")
            return None

        try:
            age = int(data["age"])
            if not 1 <= age <= 120:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Age", "Age must be a whole number between 1 and 120.")
            return None

        if data["email"] and ("@" not in data["email"] or "." not in data["email"].split("@")[-1]):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return None

        data["age"] = age
        return data

    def add_student(self):
        data = self.get_form_data()
        if data is None:
            return
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO students (roll_no, name, age, gender, course, email, phone)
                    VALUES (:roll_no, :name, :age, :gender, :course, :email, :phone)
                """, data)
            self.load_students()
            self.clear_form()
            self.status_var.set(f"Student '{data['name']}' added successfully.")
            messagebox.showinfo("Success", "Student added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Roll Number", "That roll number already exists. Use a unique roll number.")

    def update_student(self):
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student from the table before updating.")
            return
        data = self.get_form_data()
        if data is None:
            return
        data["id"] = self.selected_student_id
        try:
            with self.conn:
                self.conn.execute("""
                    UPDATE students
                    SET roll_no=:roll_no, name=:name, age=:age, gender=:gender,
                        course=:course, email=:email, phone=:phone
                    WHERE id=:id
                """, data)
            self.load_students()
            self.clear_form()
            self.status_var.set(f"Student '{data['name']}' updated successfully.")
            messagebox.showinfo("Success", "Student updated successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Roll Number", "Another student already uses that roll number.")

    def delete_student(self):
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student from the table before deleting.")
            return
        selected_name = self.vars["name"].get().strip() or "this student"
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {selected_name}?"):
            return
        with self.conn:
            self.conn.execute("DELETE FROM students WHERE id = ?", (self.selected_student_id,))
        self.load_students()
        self.clear_form()
        self.status_var.set("Student deleted successfully.")

    def load_students(self):
        query = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if query:
            pattern = f"%{query}%"
            rows = self.conn.execute("""
                SELECT id, roll_no, name, age, gender, course, email, phone
                FROM students
                WHERE roll_no LIKE ? OR name LIKE ? OR course LIKE ? OR email LIKE ?
                ORDER BY name COLLATE NOCASE
            """, (pattern, pattern, pattern, pattern)).fetchall()
        else:
            rows = self.conn.execute("""
                SELECT id, roll_no, name, age, gender, course, email, phone
                FROM students ORDER BY name COLLATE NOCASE
            """).fetchall()

        for row in rows:
            self.tree.insert("", "end", values=tuple("" if value is None else value for value in row))
        self.status_var.set(f"{len(rows)} student record(s) shown.")

    def on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_student_id = int(values[0])
        keys = ("roll_no", "name", "age", "gender", "course", "email", "phone")
        for key, value in zip(keys, values[1:]):
            self.vars[key].set(value)

    def clear_form(self):
        self.selected_student_id = None
        for key, var in self.vars.items():
            var.set("Prefer not to say" if key == "gender" else "")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def clear_search(self):
        self.search_var.set("")
        self.load_students()

    def close_app(self):
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
