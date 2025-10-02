from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import hashlib
import json

from .models import (
    Badge, StudentPoints, PointTransaction, StudentBadge,
    Notification, StudentSkill, CareerRecommendation,
    Course, Room, TimeSlot, TimetableEntry,
    Certificate, AnalyticsSnapshot
)
from college_app.models import Assignment, Submission, FeeStructure, Payment
from attendance_app.models import Attendance


@login_required
def gamification_dashboard(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Gamification dashboard is only for students')
        return redirect('dashboard')
    
    student_points, created = StudentPoints.objects.get_or_create(student=request.user)
    
    leaderboard = StudentPoints.objects.filter(
        student__profile__role='student'
    ).select_related('student').order_by('-total_points')[:10]
    
    for rank, entry in enumerate(leaderboard, 1):
        entry.rank = rank
        entry.save()
    
    my_badges = StudentBadge.objects.filter(student=request.user).select_related('badge')
    available_badges = Badge.objects.filter(is_active=True).exclude(
        id__in=my_badges.values_list('badge_id', flat=True)
    )
    
    recent_transactions = PointTransaction.objects.filter(
        student=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'student_points': student_points,
        'leaderboard': leaderboard,
        'my_badges': my_badges,
        'available_badges': available_badges,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'advanced_features/gamification_dashboard.html', context)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'advanced_features/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


@login_required
def career_guidance(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Career guidance is only for students')
        return redirect('dashboard')
    
    skills = StudentSkill.objects.filter(student=request.user)
    recommendations = CareerRecommendation.objects.filter(student=request.user)
    
    if not recommendations.exists() and request.method == 'POST':
        generate_career_recommendations(request.user)
        return redirect('career_guidance')
    
    context = {
        'skills': skills,
        'recommendations': recommendations,
    }
    return render(request, 'advanced_features/career_guidance.html', context)


def generate_career_recommendations(student):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    skills = StudentSkill.objects.filter(student=student)
    skill_text = ' '.join([s.skill_name for s in skills])
    
    career_database = [
        {'path': 'Software Engineer', 'skills': 'python programming java javascript algorithms data structures', 'salary': '$80,000 - $150,000'},
        {'path': 'Data Scientist', 'skills': 'python machine learning statistics pandas numpy scikit-learn', 'salary': '$90,000 - $160,000'},
        {'path': 'Web Developer', 'skills': 'html css javascript react angular node web design', 'salary': '$60,000 - $120,000'},
        {'path': 'DevOps Engineer', 'skills': 'linux docker kubernetes aws cloud automation ci cd', 'salary': '$85,000 - $145,000'},
        {'path': 'Mobile Developer', 'skills': 'java kotlin swift android ios mobile app development', 'salary': '$75,000 - $135,000'},
        {'path': 'Cybersecurity Analyst', 'skills': 'security networking penetration testing cryptography ethical hacking', 'salary': '$80,000 - $140,000'},
        {'path': 'Cloud Architect', 'skills': 'aws azure gcp cloud architecture microservices scalability', 'salary': '$100,000 - $180,000'},
        {'path': 'AI/ML Engineer', 'skills': 'python tensorflow pytorch deep learning neural networks nlp', 'salary': '$95,000 - $170,000'},
    ]
    
    if not skill_text.strip():
        skill_text = 'general computer science programming'
    
    documents = [skill_text] + [c['skills'] for c in career_database]
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        for i, career in enumerate(career_database):
            match_percentage = min(cosine_similarities[i] * 100, 99.99)
            if match_percentage < 10:
                match_percentage = max(match_percentage, 25)
            
            CareerRecommendation.objects.create(
                student=student,
                career_path=career['path'],
                match_percentage=match_percentage,
                description=f"Exciting career in {career['path']} with strong industry demand.",
                required_skills=career['skills'],
                salary_range=career['salary'],
                job_outlook="Growing field with excellent opportunities",
                recommended_courses="Relevant online courses and certifications available"
            )
    except Exception as e:
        CareerRecommendation.objects.create(
            student=student,
            career_path='Software Engineer',
            match_percentage=70.00,
            description='Versatile career path with many opportunities',
            required_skills='programming, problem solving, teamwork',
            salary_range='$70,000 - $140,000',
            job_outlook='Strong growth expected',
            recommended_courses='Computer Science fundamentals'
        )


@login_required
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        skill_category = request.POST.get('skill_category')
        proficiency = request.POST.get('proficiency', 'beginner')
        
        StudentSkill.objects.get_or_create(
            student=request.user,
            skill_name=skill_name,
            defaults={
                'skill_category': skill_category,
                'proficiency_level': proficiency
            }
        )
        messages.success(request, f'Skill "{skill_name}" added successfully!')
        
    return redirect('career_guidance')


@login_required
def timetable_view(request):
    if request.user.profile.role == 'teacher':
        entries = TimetableEntry.objects.filter(
            teacher=request.user, 
            is_active=True
        ).select_related('course', 'room', 'time_slot').order_by('time_slot__day_of_week', 'time_slot__start_time')
    elif request.user.profile.role == 'admin':
        entries = TimetableEntry.objects.filter(
            is_active=True
        ).select_related('course', 'teacher', 'room', 'time_slot').order_by('time_slot__day_of_week', 'time_slot__start_time')
    else:
        messages.error(request, 'Timetable access restricted')
        return redirect('dashboard')
    
    timetable = {}
    for entry in entries:
        day = entry.time_slot.day_of_week
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(entry)
    
    context = {
        'timetable': timetable,
        'entries': entries,
    }
    return render(request, 'advanced_features/timetable.html', context)


@login_required
def generate_timetable(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can generate timetables')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            from ortools.sat.python import cp_model
            
            courses = list(Course.objects.all())
            rooms = list(Room.objects.all())
            teachers = list(User.objects.filter(profile__role='teacher'))
            time_slots = list(TimeSlot.objects.all())
            
            model = cp_model.CpModel()
            
            assignments = {}
            for course in courses:
                for room in rooms:
                    for time_slot in time_slots:
                        for teacher in teachers:
                            assignments[(course, room, time_slot, teacher)] = model.NewBoolVar(
                                f'assign_{course.id}_{room.id}_{time_slot.id}_{teacher.id}'
                            )
            
            for course in courses:
                model.Add(sum(assignments[(course, room, slot, teacher)] 
                            for room in rooms 
                            for slot in time_slots 
                            for teacher in teachers) >= 1)
            
            for room in rooms:
                for slot in time_slots:
                    model.Add(sum(assignments[(course, room, slot, teacher)] 
                                for course in courses 
                                for teacher in teachers) <= 1)
            
            for teacher in teachers:
                for slot in time_slots:
                    model.Add(sum(assignments[(course, room, slot, teacher)] 
                                for course in courses 
                                for room in rooms) <= 1)
            
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 30
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                TimetableEntry.objects.filter(is_active=True).update(is_active=False)
                
                for (course, room, slot, teacher), var in assignments.items():
                    if solver.Value(var) == 1:
                        TimetableEntry.objects.create(
                            course=course,
                            teacher=teacher,
                            room=room,
                            time_slot=slot,
                            academic_year='2025-2026',
                            semester=1,
                            is_active=True
                        )
                
                messages.success(request, 'Timetable generated successfully!')
            else:
                messages.warning(request, 'Could not generate optimal timetable. Manual adjustments may be needed.')
        
        except Exception as e:
            messages.error(request, f'Error generating timetable: {str(e)}')
    
    return redirect('timetable_view')


@login_required
def my_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).order_by('-issue_date')
    
    context = {
        'certificates': certificates,
    }
    return render(request, 'advanced_features/certificates.html', context)


@login_required
def issue_certificate(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can issue certificates')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        cert_type = request.POST.get('certificate_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        student = get_object_or_404(User, id=student_id)
        
        cert_data = f"{student.username}|{title}|{datetime.now().isoformat()}"
        cert_hash = hashlib.sha256(cert_data.encode()).hexdigest()
        
        certificate = Certificate.objects.create(
            student=student,
            certificate_type=cert_type,
            title=title,
            description=description,
            certificate_hash=cert_hash,
            is_verified=True,
            metadata={
                'issued_by': request.user.username,
                'issue_timestamp': datetime.now().isoformat()
            }
        )
        
        Notification.objects.create(
            user=student,
            notification_type='system',
            title='Certificate Issued',
            message=f'You have been awarded: {title}',
            link=f'/advanced/certificates/'
        )
        
        messages.success(request, f'Certificate issued to {student.username}')
        return redirect('issue_certificate')
    
    students = User.objects.filter(profile__role='student').order_by('username')
    context = {
        'students': students,
    }
    return render(request, 'advanced_features/issue_certificate.html', context)


@login_required
def analytics_dashboard(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can access analytics')
        return redirect('dashboard')
    
    total_students = User.objects.filter(profile__role='student').count()
    total_teachers = User.objects.filter(profile__role='teacher').count()
    
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    attendance_avg = Attendance.objects.filter(
        date__gte=last_30_days
    ).count() / max(total_students, 1)
    
    total_assignments = Assignment.objects.count()
    completed_submissions = Submission.objects.filter(marks_obtained__isnull=False).count()
    assignment_completion = (completed_submissions / max(total_assignments * total_students, 1)) * 100
    
    total_fees = FeeStructure.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    paid_fees = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    fee_collection_rate = (paid_fees / max(total_fees, 1)) * 100 if total_fees > 0 else 0
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'attendance_average': round(attendance_avg, 2),
        'assignment_completion_rate': round(assignment_completion, 2),
        'fee_collection_rate': round(fee_collection_rate, 2),
    }
    return render(request, 'advanced_features/analytics.html', context)


def award_points(student, points, reason, category='bonus'):
    student_points, created = StudentPoints.objects.get_or_create(student=student)
    
    PointTransaction.objects.create(
        student=student,
        points=points,
        reason=reason,
        category=category
    )
    
    student_points.total_points += points
    
    if category == 'attendance':
        student_points.attendance_points += points
    elif category == 'assignment':
        student_points.assignment_points += points
    elif category == 'participation':
        student_points.participation_points += points
    
    student_points.save()
    
    check_and_award_badges(student)
    
    Notification.objects.create(
        user=student,
        notification_type='badge_earned',
        title=f'Earned {points} Points!',
        message=f'You earned {points} points for: {reason}',
        link='/advanced/gamification/'
    )


def check_and_award_badges(student):
    student_points = StudentPoints.objects.get(student=student)
    available_badges = Badge.objects.filter(
        is_active=True,
        points_required__lte=student_points.total_points
    ).exclude(
        id__in=StudentBadge.objects.filter(student=student).values_list('badge_id', flat=True)
    )
    
    for badge in available_badges:
        StudentBadge.objects.create(student=student, badge=badge)
        Notification.objects.create(
            user=student,
            notification_type='badge_earned',
            title='New Badge Earned!',
            message=f'Congratulations! You earned the "{badge.name}" badge!',
            link='/advanced/gamification/'
        )
