from django.urls import path
from . import views
from . import chatbot_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('manage/create-invite/', views.create_user_invite, name='create_invite'),
    path('manage/invites/', views.manage_invites, name='manage_invites'),
    path('manage/delete-invite/<int:invite_id>/', views.delete_invite, name='delete_invite'),
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    
    # Admin - Fee Management
    path('manage/fee-structures/', views.manage_fee_structures, name='manage_fee_structures'),
    path('manage/create-fee-structure/', views.create_fee_structure, name='create_fee_structure'),
    path('manage/delete-fee-structure/<int:fee_id>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('manage/payments/', views.view_all_payments, name='view_all_payments'),
    
    # Student - Fee Payment
    path('student/fees/', views.view_student_fees, name='view_student_fees'),
    path('student/make-payment/<int:fee_id>/', views.make_payment, name='make_payment'),
    path('student/verify-payment/', views.verify_payment, name='verify_payment'),
    path('student/payment-success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('student/payment-history/', views.view_payment_history, name='view_payment_history'),
    
    # Notices and Bulletins - View Only
    path('notices/', views.view_notices, name='view_notices'),
    path('bulletins/', views.view_bulletins, name='view_bulletins'),
    
    # Admin - Notice Management
    path('manage/notices/', views.manage_notices, name='manage_notices'),
    path('manage/create-notice/', views.create_notice, name='create_notice'),
    path('manage/edit-notice/<int:notice_id>/', views.edit_notice, name='edit_notice'),
    path('manage/delete-notice/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    
    # Admin - Bulletin Management
    path('manage/bulletins/', views.manage_bulletins, name='manage_bulletins'),
    path('manage/create-bulletin/', views.create_bulletin, name='create_bulletin'),
    path('manage/edit-bulletin/<int:bulletin_id>/', views.edit_bulletin, name='edit_bulletin'),
    path('manage/delete-bulletin/<int:bulletin_id>/', views.delete_bulletin, name='delete_bulletin'),
    
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
    
    # Chatbot
    path('chatbot/query/', chatbot_views.chatbot_query, name='chatbot_query'),
    
    # Admin - College Information Management
    path('manage/colleges/', chatbot_views.manage_colleges, name='manage_colleges'),
    path('manage/create-college/', chatbot_views.create_college, name='create_college'),
    path('manage/edit-college/<int:college_id>/', chatbot_views.edit_college, name='edit_college'),
    path('manage/delete-college/<int:college_id>/', chatbot_views.delete_college, name='delete_college'),
]
