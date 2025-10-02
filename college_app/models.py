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
    
    SEMESTER_CHOICES = (
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    course = models.CharField(max_length=100, blank=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, null=True, blank=True)
    
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


class FeeStructure(models.Model):
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ${self.amount}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='cash')
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.fee_structure.name} - ${self.amount}"


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=20, choices=Profile.ROLE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Bulletin(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='bulletins/', blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class BusRoute(models.Model):
    route_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    stops = models.TextField(help_text="Comma-separated list of stops")
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"Route {self.route_number} - {self.name}"


class BusLocation(models.Model):
    bus_route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    current_stop = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bus_route.route_number} - {self.updated_at}"


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class CollegeInfo(models.Model):
    name = models.CharField(max_length=300, unique=True)
    location = models.CharField(max_length=200)
    established_year = models.IntegerField(null=True, blank=True)
    college_type = models.CharField(max_length=100, blank=True)
    placement_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hostel_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admission_process = models.TextField(blank=True)
    courses_offered = models.TextField(blank=True)
    facilities = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'College Information'
    
    def __str__(self):
        return self.name
