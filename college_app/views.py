from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, UserInvite


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        temp_password = request.POST.get('temp_password')
        
        try:
            invite = UserInvite.objects.get(username=username, status='pending')
            
            if invite.temporary_password != temp_password:
                messages.error(request, 'Invalid temporary password. Please check the credentials provided by admin.')
                return render(request, 'college_app/signup.html')
            
            if invite.email != email:
                messages.error(request, 'Email does not match the invite. Please use the email provided by admin.')
                return render(request, 'college_app/signup.html')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'college_app/signup.html')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user, role=invite.role)
            
            invite.status = 'activated'
            invite.save()
            
            messages.success(request, 'Account activated successfully! Please login.')
            return redirect('login')
        
        except UserInvite.DoesNotExist:
            messages.error(request, 'No invite found for this username. Please contact admin.')
            return render(request, 'college_app/signup.html')
    
    return render(request, 'college_app/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'college_app/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    profile = request.user.profile
    context = {
        'user': request.user,
        'role': profile.role,
    }
    return render(request, 'college_app/dashboard.html', context)


@login_required
def create_user_invite(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can create user invites')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        
        if UserInvite.objects.filter(username=username).exists():
            messages.error(request, 'An invite for this username already exists')
            return render(request, 'college_app/create_invite.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken')
            return render(request, 'college_app/create_invite.html')
        
        temp_password = UserInvite.generate_temp_password()
        
        UserInvite.objects.create(
            username=username,
            email=email,
            role=role,
            temporary_password=temp_password,
            created_by=request.user
        )
        
        messages.success(request, f'Invite created! Username: {username}, Temporary Password: {temp_password}')
        return redirect('manage_invites')
    
    return render(request, 'college_app/create_invite.html')


@login_required
def manage_invites(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can manage user invites')
        return redirect('dashboard')
    
    invites = UserInvite.objects.all().order_by('-created_at')
    return render(request, 'college_app/manage_invites.html', {'invites': invites})


@login_required
def delete_invite(request, invite_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can delete invites')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            invite = UserInvite.objects.get(id=invite_id)
            invite.delete()
            messages.success(request, 'Invite deleted successfully')
        except UserInvite.DoesNotExist:
            messages.error(request, 'Invite not found')
    
    return redirect('manage_invites')
