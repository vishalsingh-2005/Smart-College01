from django.db import models
from django.contrib.auth.models import User

class FaceEncoding(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_encoding', limit_choices_to={'profile__role': 'student'})
    encoding = models.BinaryField()
    image = models.ImageField(upload_to='face_images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Face encoding for {self.student.username}"

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records', limit_choices_to={'profile__role': 'student'})
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='present')
    
    class Meta:
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"
