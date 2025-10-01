from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('manage/create-invite/', views.create_user_invite, name='create_invite'),
    path('manage/invites/', views.manage_invites, name='manage_invites'),
    path('manage/delete-invite/<int:invite_id>/', views.delete_invite, name='delete_invite'),
    
    # Admin - Fee Management
    path('manage/fee-structures/', views.manage_fee_structures, name='manage_fee_structures'),
    path('manage/create-fee-structure/', views.create_fee_structure, name='create_fee_structure'),
    path('manage/delete-fee-structure/<int:fee_id>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('manage/payments/', views.view_all_payments, name='view_all_payments'),
    
    # Student - Fee Payment
    path('student/fees/', views.view_student_fees, name='view_student_fees'),
    path('student/make-payment/<int:fee_id>/', views.make_payment, name='make_payment'),
    path('student/payment-history/', views.view_payment_history, name='view_payment_history'),
    
    # Notices and Bulletins
    path('notices/', views.view_notices, name='view_notices'),
    path('bulletins/', views.view_bulletins, name='view_bulletins'),
    
    # Student - Bus Tracker
    path('student/bus-tracker/', views.view_bus_tracker, name='view_bus_tracker'),
    
    # Student - Assignments
    path('student/assignments/', views.view_assignments, name='view_assignments'),
    path('student/submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    
    # Teacher - Assignments
    path('teacher/create-assignment/', views.create_assignment, name='create_assignment'),
    path('teacher/assignments/', views.view_teacher_assignments, name='view_teacher_assignments'),
    path('teacher/grade-assignment/<int:submission_id>/', views.grade_assignment, name='grade_assignment'),
    path('teacher/view-submissions/<int:assignment_id>/', views.view_assignment_submissions, name='view_assignment_submissions'),
]
