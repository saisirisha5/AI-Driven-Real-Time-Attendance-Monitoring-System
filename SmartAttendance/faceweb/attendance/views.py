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
    error_message = None  # for inline display instead of Django messages

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            return redirect('homepage')  # redirect to dashboard
        else:
            error_message = "❌ Invalid credentials. Please try again."

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

            # If a new image is uploaded, replace it
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
            messages.success(request, "✅ Student record updated successfully.")
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
    selected_name = request.GET.get('name')

    # Default to today’s date if none selected
    today = datetime.now().strftime("%Y-%m-%d")
    target_date = selected_date or today

    # --- Fetch all students ---
    student_ref = db.collection('students').stream()
    student_data = [s.to_dict() for s in student_ref]
    student_images = {s.get('name'): s.get('image_base64') for s in student_data}
    total_students = len(student_data)

    # --- Fetch attendance records for that date ---
    attendance_ref = db.collection('attendance_records').where('date', '==', target_date).stream()
    attendance_data = [r.to_dict() for r in attendance_ref]

    # --- Apply name filter ---
    if selected_name:
        attendance_data = [r for r in attendance_data if selected_name.lower() in r.get('name', '').lower()]

    # --- Build attendance status map ---
    present_students = {r['name']: r for r in attendance_data if r.get('status', 'Present') == 'Present'}
    all_names = {s['name'] for s in student_data}
    absent_students = all_names - set(present_students.keys())

    # --- Combine into a unified student list ---
    students = []

    # Present students
    for name, record in present_students.items():
        students.append({
            'name': name,
            'last_timestamp': record.get('timestamp'),
            'image_base64': student_images.get(name),
            'status': 'Present'
        })

    # Absent students
    for name in absent_students:
        students.append({
            'name': name,
            'last_timestamp': 'N/A',
            'image_base64': student_images.get(name),
            'status': 'Absent'
        })

    # --- Attendance analytics ---
    todays_present = len(present_students)
    todays_absent = len(absent_students)

    # Monthly analytics (approximate for now)
    month_str = datetime.now().strftime("%Y-%m")
    monthly_records = db.collection('attendance_records').where('date', '>=', f"{month_str}-01").stream()
    monthly_records = [r.to_dict() for r in monthly_records]
    monthly_present = len({f"{r['name']}-{r['date']}" for r in monthly_records if r.get('status', 'Present') == 'Present'})
    monthly_percentage = round((monthly_present / (total_students * 30)) * 100, 2) if total_students else 0

    # --- Context ---
    context = {
        'students': students,
        'selected_date': target_date,
        'selected_name': selected_name,
        'total_students': total_students,
        'todays_present': todays_present,
        'todays_absent': todays_absent,
        'monthly_percentage': monthly_percentage,
    }

    return render(request, 'view_attendance.html', context)


def delete_student(request, regd_no):
    """Delete a student record."""
    try:
        db.collection('students').document(regd_no).delete()
        messages.success(request, "🗑️ Student deleted successfully.")
    except Exception as e:
        messages.error(request, f"❌ Failed to delete student: {e}")
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

    print(f"📅 Running absentee marking job for {today_str}...")

    # Step 1: Fetch all students
    students_ref = db.collection('students').stream()
    all_students = {s.to_dict()['regd_no']: s.to_dict() for s in students_ref}
    print(f"✅ Total students found: {len(all_students)}")

    # Step 2: Fetch today's attendance records
    attendance_ref = db.collection('attendance_records').where('date', '==', today_str).stream()
    present_regd = {r.to_dict()['regd_no'] for r in attendance_ref}

    # Step 3: Mark absentees
    absentees = [s for s in all_students.values() if s['regd_no'] not in present_regd]
    print(f"⚠️ Students absent today: {len(absentees)}")

    for student in absentees:
        db.collection('attendance_records').add({
            'name': student['name'],
            'regd_no': student['regd_no'],
            'date': today_str,
            'time': END_TIME,
            'status': 'Absent',
            'timestamp': datetime.now(),
        })

    print("✅ Absentee marking completed.")