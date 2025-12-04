from flask import Flask, render_template, request
import os

# ---------------------------
# FILE SETUP
# ---------------------------
DATA_DIR = "data"
STUDENT_FILE = os.path.join(DATA_DIR, "students.txt")
GRADES_FILE = os.path.join(DATA_DIR, "grades.txt")

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

students = {}   # Loaded from files


# ---------------------------
# LOAD DATA
# ---------------------------
def load_data():
    global students
    students = {}

    # Load students
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                sid, first, last, dob = line.split("|")
                students[sid] = {
                    "first": first,
                    "last": last,
                    "dob": dob,
                    "grades": []
                }

    # Load grades
    if os.path.exists(GRADES_FILE):
        with open(GRADES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                sid, grade_str = line.split("|")
                if grade_str:
                    students[sid]["grades"] = [float(x) for x in grade_str.split(",")]
                else:
                    students[sid]["grades"] = []


# ---------------------------
# SAVE DATA
# ---------------------------
def save_data():
    # Save students
    with open(STUDENT_FILE, "w") as f:
        for sid, s in students.items():
            f.write(f"{sid}|{s['first']}|{s['last']}|{s['dob']}\n")

    # Save grades
    with open(GRADES_FILE, "w") as f:
        for sid, s in students.items():
            grade_str = ",".join(str(g) for g in s["grades"])
            f.write(f"{sid}|{grade_str}\n")


# ---------------------------
# FLASK APP
# ---------------------------
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    result = None

    # Determine which section to show
    section = request.args.get("section", "add-student")

    # -----------------------------------
    # ADD STUDENT
    # -----------------------------------
    if request.form.get("action") == "add_student":
        sid = request.form.get("sid")
        first = request.form.get("first")
        last = request.form.get("last")
        dob = request.form.get("dob")

        if sid in students:
            message = "Student ID already exists."
        else:
            students[sid] = {
                "first": first,
                "last": last,
                "dob": dob,
                "grades": []
            }
            save_data()
            message = "Student added."

        section = "add-student"

    # -----------------------------------
    # EDIT STUDENT
    # -----------------------------------
    elif request.form.get("action") == "edit_student":
        sid = request.form.get("edit_sid")

        if sid not in students:
            message = "Student not found."
        else:
            if request.form.get("edit_first"):
                students[sid]["first"] = request.form.get("edit_first")

            if request.form.get("edit_last"):
                students[sid]["last"] = request.form.get("edit_last")

            if request.form.get("edit_dob"):
                students[sid]["dob"] = request.form.get("edit_dob")

            save_data()
            message = "Student updated."

        section = "edit-student"

    # -----------------------------------
    # DELETE STUDENT
    # -----------------------------------
    elif request.form.get("action") == "delete_student":
        sid = request.form.get("delete_sid")

        if sid in students:
            del students[sid]
            save_data()
            message = "Student deleted."
        else:
            message = "Student not found."

        section = "delete-student"

    # -----------------------------------
    # ADD GRADE
    # -----------------------------------
    elif request.form.get("action") == "add_grade":
        sid = request.form.get("grade_sid")
        grade = request.form.get("grade_value")

        if sid in students:
            students[sid]["grades"].append(float(grade))
            save_data()
            message = "Grade added."
        else:
            message = "Student not found."

        section = "add-grade"

    # -----------------------------------
    # EDIT GRADE
    # -----------------------------------
    elif request.form.get("action") == "edit_grade":
        sid = request.form.get("edit_grade_sid")
        index = int(request.form.get("grade_index"))
        new_value = float(request.form.get("new_grade"))

        if sid not in students:
            message = "Student not found."
        elif index < 0 or index >= len(students[sid]["grades"]):
            message = "Invalid grade index."
        else:
            students[sid]["grades"][index] = new_value
            save_data()
            message = "Grade updated."

        section = "edit-grade"

    # -----------------------------------
    # DELETE GRADE
    # -----------------------------------
    elif request.form.get("action") == "delete_grade":
        sid = request.form.get("delete_grade_sid")
        index = int(request.form.get("delete_grade_index"))

        if sid not in students:
            message = "Student not found."
        elif index < 0 or index >= len(students[sid]["grades"]):
            message = "Invalid grade index."
        else:
            students[sid]["grades"].pop(index)
            save_data()
            message = "Grade deleted."

        section = "delete-grade"

    # -----------------------------------
    # VIEW AVERAGE
    # -----------------------------------
    elif request.form.get("action") == "view_average":
        sid = request.form.get("avg_sid")

        if sid not in students or not students[sid]["grades"]:
            result = "No grades available."
        else:
            avg = sum(students[sid]["grades"]) / len(students[sid]["grades"])
            student = students[sid]
            result = f"{student['first']} {student['last']} → Average: {avg:.2f}"

        section = "view-average"

    # -----------------------------------
    # HIGHEST SCORER
    # -----------------------------------
    elif request.form.get("action") == "highest":
        best = -1
        top = None

        for sid, s in students.items():
            if s["grades"]:
                avg = sum(s["grades"]) / len(s["grades"])
                if avg > best:
                    best = avg
                    top = sid

        if top:
            student = students[top]
            result = f"{student['first']} {student['last']} → {best:.2f}"
        else:
            result = "No grades available."

        section = "highest-scorer"

    return render_template("index.html",
                           students=students,
                           message=message,
                           result=result,
                           section=section)


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    load_data()
    app.run(debug=True)
