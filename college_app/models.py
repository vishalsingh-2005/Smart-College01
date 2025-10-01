from django.db import models
from django.contrib.auth.models import User
import secrets

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('doctor', 'Doctor'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class UserInvite(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('activated', 'Activated'),
        ('expired', 'Expired'),
    )
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=Profile.ROLE_CHOICES)
    temporary_password = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.role} ({self.status})"
    
    @staticmethod
    def generate_temp_password():
        return secrets.token_urlsafe(12)
