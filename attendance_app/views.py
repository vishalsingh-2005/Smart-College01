from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
