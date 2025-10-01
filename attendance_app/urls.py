from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.view_attendance, name='view_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('mark/', views.mark_attendance_manual, name='mark_attendance_manual'),
    path('api/mark/', views.mark_attendance_api, name='mark_attendance_api'),
]
