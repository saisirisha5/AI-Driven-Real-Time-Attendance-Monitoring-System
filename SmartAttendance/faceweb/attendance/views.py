from django.shortcuts import render, redirect
from .forms import FaceForm
from .firebase_config import db
from django.conf import settings
import os
from .forms import FaceForm
from .firebase_utils import add_student_to_firebase
from django.contrib import messages


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


def view_attendance(request):
    print("Fetching attendance data...")

    # Fetch attendance records
    attendance_ref = db.collection('attendance_records').stream()
    attendance_data = [r.to_dict() for r in attendance_ref]

    latest_attendance = {}
    for record in attendance_data:
        name = record.get('name')
        timestamp = record.get('timestamp')
        if name:
            if name not in latest_attendance or timestamp > latest_attendance[name]:
                latest_attendance[name] = timestamp

    # Fetch student images from 'students' collection
    student_ref = db.collection('students').stream()
    student_images = {s.to_dict().get('name'): s.to_dict().get('image_base64') for s in student_ref}

    # Combine both
    students = []
    for name, timestamp in latest_attendance.items():
        students.append({
            'name': name,
            'last_timestamp': timestamp,
            'image_base64': student_images.get(name)
        })

    return render(request, 'view_attendance.html', {'students': students})

def student_detail(request, name):
    records = db.collection('attendance_records').where('name', '==', name).stream()
    attendance_history = [r.to_dict() for r in records]
    attendance_history.sort(key=lambda x: x['timestamp'], reverse=True)
    return render(request, 'student_detail.html', {'name': name, 'history': attendance_history})

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
