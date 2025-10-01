from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import HealthRecord, Appointment

@login_required
def add_health_record(request):
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Only doctors can add health records')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        description = request.POST.get('description')
        diagnosis = request.POST.get('diagnosis')
        prescription = request.POST.get('prescription')
        
        student = get_object_or_404(User, id=student_id, profile__role='student')
        HealthRecord.objects.create(
            student=student,
            doctor=request.user,
            description=description,
            diagnosis=diagnosis,
            prescription=prescription
        )
        messages.success(request, 'Health record added successfully!')
        return redirect('view_health_records')
    
    students = User.objects.filter(profile__role='student')
    return render(request, 'healthcare_app/add_record.html', {'students': students})

@login_required
def view_health_records(request):
    profile = request.user.profile
    
    if profile.role == 'student':
        records = HealthRecord.objects.filter(student=request.user).order_by('-date')
    elif profile.role == 'doctor':
        records = HealthRecord.objects.filter(doctor=request.user).order_by('-date')
    else:
        records = HealthRecord.objects.all().order_by('-date')
    
    return render(request, 'healthcare_app/view_records.html', {'records': records})

@login_required
def book_appointment(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can book appointments')
        return redirect('dashboard')
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        appointment_date = request.POST.get('appointment_date')
        reason = request.POST.get('reason')
        
        doctor = get_object_or_404(User, id=doctor_id, profile__role='doctor')
        Appointment.objects.create(
            student=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            reason=reason
        )
        messages.success(request, 'Appointment booked successfully!')
        return redirect('view_appointments')
    
    doctors = User.objects.filter(profile__role='doctor')
    return render(request, 'healthcare_app/book_appointment.html', {'doctors': doctors})

@login_required
def view_appointments(request):
    profile = request.user.profile
    
    if profile.role == 'student':
        appointments = Appointment.objects.filter(student=request.user).order_by('-appointment_date')
    elif profile.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=request.user).order_by('-appointment_date')
    else:
        appointments = Appointment.objects.all().order_by('-appointment_date')
    
    return render(request, 'healthcare_app/view_appointments.html', {'appointments': appointments})
