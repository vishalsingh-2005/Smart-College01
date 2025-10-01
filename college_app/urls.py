from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/create-invite/', views.create_user_invite, name='create_invite'),
    path('admin/manage-invites/', views.manage_invites, name='manage_invites'),
    path('admin/delete-invite/<int:invite_id>/', views.delete_invite, name='delete_invite'),
]
