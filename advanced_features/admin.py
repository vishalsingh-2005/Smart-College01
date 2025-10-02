from django.contrib import admin
from .models import (
    Badge, StudentPoints, PointTransaction, StudentBadge,
    Notification, StudentSkill, CareerRecommendation,
    Course, Room, TimeSlot, TimetableEntry,
    Certificate, AnalyticsSnapshot
)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'badge_type', 'points_required', 'is_active']
    list_filter = ['badge_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(StudentPoints)
class StudentPointsAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_points', 'rank', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['student__username']
    ordering = ['-total_points']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['student', 'points', 'category', 'reason', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['student__username', 'reason']


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ['student', 'badge', 'earned_at']
    list_filter = ['badge', 'earned_at']
    search_fields = ['student__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ['student', 'skill_name', 'skill_category', 'proficiency_level', 'acquired_date']
    list_filter = ['proficiency_level', 'skill_category']
    search_fields = ['student__username', 'skill_name']


@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'career_path', 'match_percentage', 'created_at']
    list_filter = ['created_at']
    search_fields = ['student__username', 'career_path']
    ordering = ['-match_percentage']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'semester', 'credits', 'department', 'max_students']
    list_filter = ['semester', 'department']
    search_fields = ['code', 'name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'capacity', 'building', 'has_projector']
    list_filter = ['room_type', 'building', 'has_projector']
    search_fields = ['room_number']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'slot_name', 'start_time', 'end_time']
    list_filter = ['day_of_week']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher', 'room', 'time_slot', 'semester', 'is_active']
    list_filter = ['semester', 'is_active', 'academic_year']
    search_fields = ['course__code', 'teacher__username']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student', 'certificate_type', 'title', 'issue_date', 'is_verified']
    list_filter = ['certificate_type', 'is_verified', 'issue_date']
    search_fields = ['student__username', 'title', 'certificate_hash']


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ['snapshot_date', 'total_students', 'attendance_average', 'assignment_completion_rate']
    list_filter = ['snapshot_date']
