print("APP STARTED")
from flask import Flask, render_template, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "student123"
# Database Create
def init_db():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        enrollment TEXT NOT NULL,
        course TEXT NOT NULL
    )
    """)
    cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    date TEXT,
    status TEXT
)
""")
    cur.execute("""
CREATE TABLE IF NOT EXISTS marks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    subject TEXT,
    marks INTEGER
)
""")
    print("APP STARTED")
    conn.commit()
    conn.close()
init_db()
# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Add Student
@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"]
    course = request.form["course"]
    enrollment = request.form["enrollment"]
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students(name,enrollment,course) VALUES(?,?,?)",
        (name, enrollment, course)
    )

    conn.commit()
    conn.close()

    return redirect("/students")

# Student List
@app.route("/students")
def students():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    return render_template("students.html", students=data)
@app.route("/search")
def search_student():

    keyword = request.args.get("keyword")

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + keyword + '%',)
    )

    data = cur.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=data
    )
@app.route("/delete/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/students")
@app.route("/edit/<int:id>")
def edit_student(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cur.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/update/<int:id>", methods=["POST"])
def update_student(id):

    name = request.form["name"]
    enrollment = request.form["enrollment"]
    course = request.form["course"]

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE students
        SET name=?, enrollment=?, course=?
        WHERE id=?
        """,
        (name, enrollment, course, id)
    )

    conn.commit()
    conn.close()

    return redirect("/students")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/login_check", methods=["POST"])
def login_check():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["admin"] = username
        return redirect("/dashboard")

    return "Invalid Login"
@app.route("/attendance")
def attendance():

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        students=students
    )
@app.route("/edit_attendance/<int:id>")
def edit_attendance(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM attendance WHERE id=?", (id,))
    data = cur.fetchone()

    conn.close()

    return render_template("edit_attendance.html", data=data)
@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    student_name = request.form["student_name"]
    date = request.form["date"]
    status = request.form["status"]

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attendance
        (student_name,date,status)
        VALUES(?,?,?)
        """,
        (student_name,date,status)
    )

    conn.commit()
    conn.close()

    return redirect("/attendance")
@app.route("/marks")
def marks():

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    conn.close()

    return render_template(
        "marks.html",
        students=students
    )


@app.route("/save_marks", methods=["POST"])
def save_marks():

    student_name = request.form["student_name"]
    subject = request.form["subject"]
    marks = request.form["marks"]

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO marks
        (student_name,subject,marks)
        VALUES(?,?,?)
        """,
        (student_name, subject, marks)
    )

    conn.commit()
    conn.close()

    return redirect("/marks")
@app.route("/marks_report")
def marks_report():

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM marks
    ORDER BY marks DESC
""")
    data = cur.fetchall()

    conn.close()

    return render_template(
        "marks_report.html",
        data=data
    )
@app.route("/report")
def report():

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT student_name,
        COUNT(*) as total,
        SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present,
        SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END) as absent
        FROM attendance
        GROUP BY student_name
        ORDER BY student_name ASC
    """)

    data = cur.fetchall()

    conn.close()

    return render_template(
        "report.html",
        data=data
    )

@app.route("/edit_mark/<int:id>")
def edit_mark(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM marks WHERE id=?", (id,))
    mark = cur.fetchone()

    conn.close()

    return render_template("edit_mark.html", mark=mark)
@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM attendance WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/report")


@app.route("/update_mark/<int:id>", methods=["POST"])
def update_mark(id):

    student_name = request.form["student_name"]
    subject = request.form["subject"]
    marks = request.form["marks"]

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE marks SET student_name=?, subject=?, marks=? WHERE id=?",
        (student_name, subject, marks, id)
    )

    conn.commit()
    conn.close()

    return redirect("/marks_report")


@app.route("/delete_mark/<int:id>")
def delete_mark(id):

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM marks WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/marks_report")
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students
    )
# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  