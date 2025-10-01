from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
