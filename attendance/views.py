from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee, Attendance
import face_recognition
import numpy as np
import cv2
import os
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.contrib.auth import login, authenticate
# attendance/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Employee, Attendance
from datetime import datetime, timedelta
import pandas as pd




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'attendance/login.html')

@login_required
def home(request):
    return render(request, 'attendance/home.html')

@login_required
def dashboard(request):
    context = {
        'today': datetime.now().date(),
        'attendance': None
    }
    try:
        if hasattr(request.user, 'employee'):
            today_attendance = Attendance.objects.get(
                employee=request.user.employee,
                date=context['today']
            )
            context['attendance'] = today_attendance
    except Attendance.DoesNotExist:
        pass
    return render(request, 'attendance/dashboard.html', context)

@login_required
def profile(request):
    try:
        employee = request.user.employee
        context = {
            'employee': employee,
            'has_face_registered': bool(employee.face_encoding)
        }
    except Employee.DoesNotExist:
        context = {
            'employee': None,
            'has_face_registered': False
        }
    return render(request, 'attendance/profile.html', context)

@login_required
def attendance_history(request):
    if hasattr(request.user, 'employee'):
        attendances = Attendance.objects.filter(
            employee=request.user.employee
        ).order_by('-date')[:30]  # Last 30 days
        context = {'attendances': attendances}
    else:
        context = {'attendances': []}
    return render(request, 'attendance/attendance_history.html', context)

@user_passes_test(lambda u: u.is_staff)
def employee_list(request):
    employees = Employee.objects.all().select_related('user')
    context = {'employees': employees}
    return render(request, 'attendance/employee_list.html', context)

@login_required
def register_face(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        if video_file:
            # Save the uploaded video to temporary storage
            video_path = default_storage.save(video_file.name, video_file)
            full_video_path = os.path.join(default_storage.base_location, video_path)
            
            cap = cv2.VideoCapture(full_video_path)
            face_found = False
            face_encoding = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                    face_found = True
                    break
            
            cap.release()
            # Remove the temporary video file after use
            os.remove(full_video_path)
            
            if face_found:
                employee = Employee.objects.create(
                    user=request.user,
                    face_encoding=face_encoding.tobytes(),
                    registration_video=video_file
                )
                messages.success(request, 'Face registered successfully!')
            else:
                messages.error(request, 'No face detected in the video')
        else:
            messages.error(request, 'No video file provided')

    return render(request, 'attendance/register_face.html')

@login_required
def generate_report(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        
        # Generate Excel report
        attendances = Attendance.objects.filter(
            date__year=year,
            date__month=month
        ).select_related('employee__user')
        
        df = pd.DataFrame(list(attendances.values(
            'employee__user__username',
            'date',
            'time_in',
            'time_out'
        )))
        
        # Process DataFrame and create Excel file
        excel_file = f'attendance_report_{year}_{month}.xlsx'
        df.to_excel(excel_file, index=False)
        
        messages.success(request, 'Report generated successfully!')
        return redirect('download_report', filename=excel_file)
    
    return render(request, 'attendance/generate_report.html')

def download_report(request, filename):
    file_path = os.path.join('path/to/report/dir', filename)  # Adjust path to where reports are saved
    return FileResponse(open(file_path, 'rb'), as_attachment=True)