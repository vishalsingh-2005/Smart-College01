from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Badge(models.Model):
    BADGE_TYPES = (
        ('attendance', 'Attendance'),
        ('assignment', 'Assignment'),
        ('participation', 'Participation'),
        ('achievement', 'Achievement'),
        ('special', 'Special'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    icon = models.CharField(max_length=50, default='🏆')
    points_required = models.IntegerField(default=100)
    color = models.CharField(max_length=20, default='#FFD700')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['points_required']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class StudentPoints(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_points')
    total_points = models.IntegerField(default=0)
    attendance_points = models.IntegerField(default=0)
    assignment_points = models.IntegerField(default=0)
    participation_points = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Student Points'
        ordering = ['-total_points']
    
    def __str__(self):
        return f"{self.student.username} - {self.total_points} points"


class PointTransaction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField()
    reason = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=(
        ('attendance', 'Attendance'),
        ('assignment', 'Assignment'),
        ('participation', 'Participation'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.points} pts ({self.reason})"


class StudentBadge(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.badge.name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('deadline', 'Deadline'),
        ('appointment', 'Appointment'),
        ('assignment', 'Assignment'),
        ('fee_due', 'Fee Due'),
        ('announcement', 'Announcement'),
        ('badge_earned', 'Badge Earned'),
        ('system', 'System'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class StudentSkill(models.Model):
    SKILL_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    skill_category = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')
    acquired_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'skill_name']
    
    def __str__(self):
        return f"{self.student.username} - {self.skill_name} ({self.proficiency_level})"


class CareerRecommendation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_recommendations')
    career_path = models.CharField(max_length=200)
    match_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    required_skills = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True)
    job_outlook = models.TextField(blank=True)
    recommended_courses = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_percentage', '-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.career_path} ({self.match_percentage}%)"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    semester = models.IntegerField()
    credits = models.IntegerField()
    department = models.CharField(max_length=100)
    max_students = models.IntegerField(default=60)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Room(models.Model):
    ROOM_TYPES = (
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('auditorium', 'Auditorium'),
        ('seminar', 'Seminar Hall'),
    )
    
    room_number = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.IntegerField()
    building = models.CharField(max_length=100)
    has_projector = models.BooleanField(default=False)
    has_lab_equipment = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.room_number} ({self.building})"


class TimeSlot(models.Model):
    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    )
    
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_name = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ['day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.day_of_week.title()} {self.slot_name} ({self.start_time}-{self.end_time})"


class TimetableEntry(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_slots')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    semester = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [
            ['room', 'time_slot', 'is_active'],
            ['teacher', 'time_slot', 'is_active'],
        ]
        verbose_name_plural = 'Timetable Entries'
    
    def __str__(self):
        return f"{self.course.code} - {self.time_slot}"


class Certificate(models.Model):
    CERTIFICATE_TYPES = (
        ('completion', 'Course Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('degree', 'Degree Certificate'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_date = models.DateField(auto_now_add=True)
    certificate_hash = models.CharField(max_length=256, unique=True)
    blockchain_txid = models.CharField(max_length=256, blank=True, null=True)
    ipfs_hash = models.CharField(max_length=256, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.title}"


class AnalyticsSnapshot(models.Model):
    snapshot_date = models.DateField(unique=True)
    total_students = models.IntegerField(default=0)
    total_teachers = models.IntegerField(default=0)
    attendance_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assignment_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    library_usage = models.IntegerField(default=0)
    fee_collection_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-snapshot_date']
    
    def __str__(self):
        return f"Analytics - {self.snapshot_date}"
