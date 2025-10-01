from django.db import models
from django.contrib.auth.models import User

class HealthRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records', limit_choices_to={'profile__role': 'student'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_records', limit_choices_to={'profile__role': 'doctor'})
    description = models.TextField()
    diagnosis = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Health Record for {self.student.username} by Dr. {self.doctor.username}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'profile__role': 'student'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'profile__role': 'doctor'})
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment: {self.student.username} with Dr. {self.doctor.username} on {self.appointment_date}"
