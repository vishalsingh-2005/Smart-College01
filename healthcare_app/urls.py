from django.urls import path
from . import views

urlpatterns = [
    path('add-record/', views.add_health_record, name='add_health_record'),
    path('view-records/', views.view_health_records, name='view_health_records'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('view-appointments/', views.view_appointments, name='view_appointments'),
]
