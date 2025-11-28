from django.shortcuts import render, redirect
from .forms import FaceForm
from .firebase_config import db
from django.conf import settings
import os
from .forms import FaceForm
from .firebase_utils import add_student_to_firebase
from django.contrib import messages
from dotenv import load_dotenv
import base64
import tempfile
from datetime import datetime
from collections import defaultdict


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def admin_login(request):
    """
    Simple admin login page with session-based authentication.
    """
    error_message = None  

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            return redirect('homepage')  # redirect to dashboard
        else:
            error_message = "Invalid credentials. Please try again."

    return render(request, "admin_login.html", {'error_message': error_message})

def homepage(request):
    """Homepage after successful admin login."""
    if not request.session.get('admin_logged_in'):
        messages.warning(request, "Please log in first.")
        return redirect('admin_login')
    return render(request, 'homepage.html')

def admin_logout(request):
    """
    Logs out admin by clearing session.
    """
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('home')

def index(request):
    return render(request, 'index.html')

def student_list(request):
    docs = db.collection('attendance_records').stream()

    data = {}
    for doc in docs:
        record = doc.to_dict()
        name = record.get("name")
        timestamp = record.get("timestamp")
        if name in data:
            if timestamp > data[name]:
                data[name] = timestamp
        else:
            data[name] = timestamp

    students = [{'name': name, 'last_timestamp': ts} for name, ts in data.items()]
    return render(request, 'view_attendance.html', {'students': students})

def student_detail(request, name):
    """Display detailed attendance history for a single student."""
    # Fetch student data (to get their image and details)
    student_ref = db.collection('students').where('name', '==', name).stream()
    student_data = next((s.to_dict() for s in student_ref), None)

    # Fetch attendance records for that student
    records = db.collection('attendance_records').where('name', '==', name).stream()
    attendance_history = [r.to_dict() for r in records]
    attendance_history.sort(key=lambda x: x['timestamp'], reverse=True)

    return render(request, 'student_detail.html', {
        'name': name,
        'student_data': student_data,
        'history': attendance_history
    })


def add_face(request):
    if request.method == 'POST':
        form = FaceForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            regd_no = form.cleaned_data['regd_no']
            department = form.cleaned_data['department']
            image = form.cleaned_data['image']

            success, msg = add_student_to_firebase(name, regd_no, department, image)
            if success:
                messages.success(request, msg)
                return redirect('view_attendance')
            else:
                messages.error(request, msg)
    else:
        form = FaceForm()

    return render(request, 'add_face.html', {'form': form})

def view_students(request):
    """Show all registered students with details."""
    if not request.session.get('admin_logged_in'):
        messages.warning(request, "Please log in first.")
        return redirect('admin_login')

    try:
        students_ref = db.collection('students').stream()
        students = []
        for s in students_ref:
            data = s.to_dict()
            students.append({
                'name': data.get('name'),
                'regd_no': data.get('regd_no'),
                'department': data.get('department'),
                'image_base64': data.get('image_base64'),
                'created_at': data.get('created_at', '')[:10]
            })
    except Exception as e:
        messages.error(request, f"Error loading students: {e}")
        students = []

    return render(request, 'view_students.html', {'students': students})

def edit_student(request, regd_no):
    """Edit an existing student's details."""
    student_ref = db.collection('students').document(regd_no)
    student_data = student_ref.get().to_dict()

    if not student_data:
        messages.error(request, "Student not found.")
        return redirect('view_students')

    if request.method == 'POST':
        form = FaceForm(request.POST, request.FILES)
        if form.is_valid():
            updated_data = {
                'name': form.cleaned_data['name'],
                'regd_no': form.cleaned_data['regd_no'],
                'department': form.cleaned_data['department'],
            }
            if 'image' in request.FILES:
                image = request.FILES['image']
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    for chunk in image.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                with open(temp_file_path, "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                os.remove(temp_file_path)

                updated_data['image_base64'] = img_base64

            # Update Firestore record
            student_ref.update(updated_data)
            messages.success(request, "Student record updated successfully.")
            return redirect('view_students')
    else:
        form = FaceForm(initial={
            'name': student_data.get('name'),
            'regd_no': student_data.get('regd_no'),
            'department': student_data.get('department'),
        })

    return render(request, 'edit_student.html', {'form': form, 'regd_no': regd_no})


def view_attendance(request):
    print("Fetching attendance data...")

    selected_date = request.GET.get('date')
    selected_regd = request.GET.get('regd_no')

    today = datetime.now().strftime("%Y-%m-%d")

    # ---- Fetch all students ----
    students_ref = db.collection('students').stream()
    student_data = [s.to_dict() for s in students_ref]
    student_map = {s["regd_no"]: s for s in student_data}

    total_students = len(student_data)

    # -------------------------------------------------------------
    # MODE 3 — REGD NO ONLY (Show only one student's card)
    # -------------------------------------------------------------
    if selected_regd and not selected_date:
        student = student_map.get(selected_regd)

        context = {
            "mode": "card",
            "student": student,
            "selected_regd": selected_regd,
            "selected_date": selected_date,
            "total_students": total_students,
        }
        return render(request, "view_attendance.html", context)

    # -------------------------------------------------------------
    # MODE 2 — DATE ONLY (Show full attendance list)
    # -------------------------------------------------------------
    if selected_date and not selected_regd:
        target_date = selected_date

        # Fetch attendance for that date
        attendance_docs = (
            db.collection("attendance_records")
            .where("date", "==", target_date)
            .stream()
        )
        attendance_data = [r.to_dict() for r in attendance_docs]

        present_regd = {r["regd_no"] for r in attendance_data}
        all_regd = set(student_map.keys())
        absent_regd = all_regd - present_regd

        attendance_list = []

        # Present students
        for r in attendance_data:
            regd = r["regd_no"]
            st = student_map.get(regd, {})
            attendance_list.append({
                "regd_no": regd,
                "name": st.get("name"),
                "department": st.get("department"),
                "timestamp": r.get("timestamp"),
                "status": "Present",
                "image_base64": st.get("image_base64"),
            })

        # Absentees
        for regd in sorted(absent_regd):
            st = student_map.get(regd, {})
            attendance_list.append({
                "regd_no": regd,
                "name": st.get("name"),
                "department": st.get("department"),
                "timestamp": "N/A",
                "status": "Absent",
                "image_base64": st.get("image_base64"),
            })

        # Sort by regd_no
        attendance_list.sort(key=lambda x: x["regd_no"])

        context = {
            "mode": "date",
            "attendance_list": attendance_list,
            "selected_date": selected_date,
            "total_students": total_students,
        }
        return render(request, "view_attendance.html", context)

    # -------------------------------------------------------------
    # MODE 1 — NO FILTERS (Default: all registered students)
    # -------------------------------------------------------------
    student_list = sorted(student_data, key=lambda x: x["regd_no"])

    context = {
        "mode": "default",
        "students": student_list,
        "total_students": total_students,
        "selected_date": selected_date,
        "selected_regd": selected_regd,
    }
    return render(request, "view_attendance.html", context)


def delete_student(request, regd_no):
    """Delete a student record."""
    try:
        db.collection('students').document(regd_no).delete()
        messages.success(request, "Student deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete student: {e}")
    return redirect('view_students')

# Attendance window
START_TIME = os.getenv("ATTENDANCE_START_TIME", "09:20")
END_TIME = os.getenv("ATTENDANCE_END_TIME", "17:30")

def mark_absentees():
    """
    Automatically marks absent students after attendance window closes.
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    print(f"Running absentee marking job for {today_str}...")

    # Step 1: Fetch all students
    students_ref = db.collection('students').stream()
    all_students = {s.to_dict()['regd_no']: s.to_dict() for s in students_ref}
    print(f"Total students found: {len(all_students)}")

    # Step 2: Fetch today's attendance records
    attendance_ref = db.collection('attendance_records').where('date', '==', today_str).stream()
    present_regd = {r.to_dict()['regd_no'] for r in attendance_ref}

    # Step 3: Mark absentees
    absentees = [s for s in all_students.values() if s['regd_no'] not in present_regd]
    print(f"Students absent today: {len(absentees)}")

    for student in absentees:
        db.collection('attendance_records').add({
            'name': student['name'],
            'regd_no': student['regd_no'],
            'date': today_str,
            'time': END_TIME,
            'status': 'Absent',
            'timestamp': datetime.now(),
        })

    print("Absentee marking completed.")