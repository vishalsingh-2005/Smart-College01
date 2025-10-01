from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance
from datetime import date, timedelta

@login_required
def view_attendance(request):
    profile = request.user.profile
    
    if profile.role == 'student':
        attendance_records = Attendance.objects.filter(student=request.user).order_by('-date')
    else:
        attendance_records = Attendance.objects.all().order_by('-date')
    
    return render(request, 'attendance_app/view_attendance.html', {'attendance_records': attendance_records})

@login_required
def attendance_report(request):
    if request.user.profile.role not in ['admin', 'teacher']:
        return render(request, 'attendance_app/unauthorized.html')
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    recent_attendance = Attendance.objects.filter(date__gte=week_ago).order_by('-date')
    
    return render(request, 'attendance_app/report.html', {'attendance_records': recent_attendance})
