from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.view_attendance, name='view_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
]
