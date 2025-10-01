from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatMessage

@login_required
def chat_room(request, room_name):
    return render(request, 'chat_app/room.html', {
        'room_name': room_name,
        'username': request.user.username
    })

@login_required
def chat_list(request):
    profile = request.user.profile
    
    if profile.role == 'student':
        teachers = User.objects.filter(profile__role='teacher')
        chat_partners = teachers
    elif profile.role == 'teacher':
        students = User.objects.filter(profile__role='student')
        chat_partners = students
    else:
        chat_partners = []
    
    return render(request, 'chat_app/list.html', {'chat_partners': chat_partners})
