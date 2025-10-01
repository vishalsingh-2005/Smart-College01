from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Attendance
from datetime import date, timedelta
import json

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

@csrf_exempt
@require_http_methods(["POST"])
def mark_attendance_api(request):
    """
    REST API endpoint to mark attendance.
    POST data: {"username": "student_username"}
    Returns: JSON response with status
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)
        
        try:
            user = User.objects.get(username=username)
            
            if not hasattr(user, 'profile') or user.profile.role != 'student':
                return JsonResponse({'error': 'User is not a student'}, status=400)
            
            attendance, created = Attendance.objects.get_or_create(
                student=user,
                date=date.today(),
                defaults={'status': 'present'}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Attendance marked for {username}',
                    'date': str(date.today())
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': f'Attendance already marked for {username} today',
                    'date': str(date.today())
                })
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def mark_attendance_manual(request):
    if request.user.profile.role not in ['teacher', 'admin']:
        messages.error(request, 'Only teachers and admins can mark attendance')
        return redirect('dashboard')
    
    students = User.objects.filter(profile__role='student').order_by('username')
    selected_date = request.GET.get('date', str(date.today()))
    
    if request.method == 'POST':
        selected_date = request.POST.get('date', str(date.today()))
        
        for student in students:
            status_key = f'status_{student.id}'
            notes_key = f'notes_{student.id}'
            status = request.POST.get(status_key)
            notes = request.POST.get(notes_key, '')
            
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        'status': status,
                        'marked_by': request.user,
                        'notes': notes
                    }
                )
        
        messages.success(request, f'Attendance marked successfully for {selected_date}')
        return redirect('mark_attendance_manual')
    
    existing_attendance = {}
    for att in Attendance.objects.filter(date=selected_date):
        existing_attendance[att.student.id] = {
            'status': att.status,
            'notes': att.notes
        }
    
    students_data = []
    for student in students:
        full_name = f"{student.first_name} {student.last_name}".strip() or student.username
        attendance_info = existing_attendance.get(student.id, {})
        students_data.append({
            'id': student.id,
            'username': student.username,
            'full_name': full_name,
            'current_status': attendance_info.get('status', 'present'),
            'current_notes': attendance_info.get('notes', '')
        })
    
    context = {
        'students_data': students_data,
        'selected_date': selected_date,
        'status_choices': Attendance.STATUS_CHOICES,
    }
    return render(request, 'attendance_app/mark_attendance.html', context)
