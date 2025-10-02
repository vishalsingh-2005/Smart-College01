from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import uuid
from .models import (Profile, UserInvite, FeeStructure, Payment, Notice, 
                     Bulletin, BusRoute, BusLocation, Assignment, Submission, CollegeInfo)
from django.http import JsonResponse


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


@login_required
def manage_fee_structures(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can manage fee structures')
        return redirect('dashboard')
    
    fee_structures = FeeStructure.objects.all().order_by('-created_at')
    return render(request, 'college_app/manage_fee_structures.html', {'fee_structures': fee_structures})


@login_required
def create_fee_structure(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can create fee structures')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        
        FeeStructure.objects.create(
            name=name,
            amount=amount,
            description=description,
            due_date=due_date,
            created_by=request.user
        )
        
        messages.success(request, 'Fee structure created successfully')
        return redirect('manage_fee_structures')
    
    return render(request, 'college_app/create_fee_structure.html')


@login_required
def delete_fee_structure(request, fee_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can delete fee structures')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            fee = FeeStructure.objects.get(id=fee_id)
            fee.delete()
            messages.success(request, 'Fee structure deleted successfully')
        except FeeStructure.DoesNotExist:
            messages.error(request, 'Fee structure not found')
    
    return redirect('manage_fee_structures')


@login_required
def view_all_payments(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can view all payments')
        return redirect('dashboard')
    
    payments = Payment.objects.all().order_by('-payment_date')
    total_revenue = sum(p.amount for p in payments.filter(status='completed'))
    pending_amount = sum(p.amount for p in payments.filter(status='pending'))
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
    }
    return render(request, 'college_app/view_all_payments.html', context)


@login_required
def view_student_fees(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can view this page')
        return redirect('dashboard')
    
    fee_structures = FeeStructure.objects.all().order_by('-due_date')
    student_payments = Payment.objects.filter(student=request.user)
    paid_fees = student_payments.values_list('fee_structure_id', flat=True)
    
    context = {
        'fee_structures': fee_structures,
        'paid_fees': paid_fees,
    }
    return render(request, 'college_app/view_student_fees.html', context)


@login_required
def make_payment(request, fee_id):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can make payments')
        return redirect('dashboard')
    
    fee_structure = get_object_or_404(FeeStructure, id=fee_id)
    
    if Payment.objects.filter(student=request.user, fee_structure=fee_structure).exists():
        messages.error(request, 'You have already paid this fee')
        return redirect('view_student_fees')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        account_number = request.POST.get('account_number', '').strip()
        ifsc_code = request.POST.get('ifsc_code', '').strip().upper()
        
        if not account_number or not ifsc_code:
            messages.error(request, 'Account Number and IFSC Code are required')
            return render(request, 'college_app/make_payment.html', {'fee_structure': fee_structure})
        
        if not account_number.isdigit() or len(account_number) < 9 or len(account_number) > 18:
            messages.error(request, 'Invalid Account Number. It should be 9-18 digits')
            return render(request, 'college_app/make_payment.html', {'fee_structure': fee_structure})
        
        if len(ifsc_code) != 11 or not ifsc_code[:4].isalpha() or not ifsc_code[4] == '0' or not ifsc_code[5:].isalnum():
            messages.error(request, 'Invalid IFSC Code. Format: ABCD0123456')
            return render(request, 'college_app/make_payment.html', {'fee_structure': fee_structure})
        
        receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            student=request.user,
            fee_structure=fee_structure,
            amount=fee_structure.amount,
            payment_method=payment_method,
            account_number=account_number,
            ifsc_code=ifsc_code,
            status='completed',
            receipt_number=receipt_number,
            transaction_id=transaction_id
        )
        
        return redirect('payment_success', payment_id=payment.id)
    
    return render(request, 'college_app/make_payment.html', {'fee_structure': fee_structure})


@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, 'college_app/payment_success.html', {'payment': payment})


@login_required
def view_payment_history(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can view payment history')
        return redirect('dashboard')
    
    payments = Payment.objects.filter(student=request.user).order_by('-payment_date')
    total_paid = sum(p.amount for p in payments.filter(status='completed'))
    
    context = {
        'payments': payments,
        'total_paid': total_paid,
    }
    return render(request, 'college_app/view_payment_history.html', context)


@login_required
def view_notices(request):
    current_time = timezone.now()
    notices = Notice.objects.filter(
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=current_time)
    ).filter(
        Q(target_role='') | Q(target_role=request.user.profile.role)
    ).order_by('-created_at')
    
    return render(request, 'college_app/view_notices.html', {'notices': notices})


@login_required
def view_bulletins(request):
    bulletins = Bulletin.objects.all().order_by('-created_at')
    return render(request, 'college_app/view_bulletins.html', {'bulletins': bulletins})


@login_required
def manage_notices(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can manage notices')
        return redirect('dashboard')
    
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'college_app/manage_notices.html', {'notices': notices})


@login_required
def create_notice(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can create notices')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        target_role = request.POST.get('target_role', '')
        expires_at = request.POST.get('expires_at')
        
        Notice.objects.create(
            title=title,
            content=content,
            posted_by=request.user,
            target_role=target_role,
            expires_at=expires_at if expires_at else None
        )
        
        messages.success(request, 'Notice created successfully')
        return redirect('manage_notices')
    
    return render(request, 'college_app/create_notice.html')


@login_required
def edit_notice(request, notice_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can edit notices')
        return redirect('dashboard')
    
    notice = get_object_or_404(Notice, id=notice_id)
    
    if request.method == 'POST':
        notice.title = request.POST.get('title')
        notice.content = request.POST.get('content')
        notice.target_role = request.POST.get('target_role', '')
        expires_at = request.POST.get('expires_at')
        notice.expires_at = expires_at if expires_at else None
        notice.is_active = request.POST.get('is_active') == 'on'
        notice.save()
        
        messages.success(request, 'Notice updated successfully')
        return redirect('manage_notices')
    
    return render(request, 'college_app/edit_notice.html', {'notice': notice})


@login_required
def delete_notice(request, notice_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can delete notices')
        return redirect('dashboard')
    
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    messages.success(request, 'Notice deleted successfully')
    return redirect('manage_notices')


@login_required
def manage_bulletins(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can manage bulletins')
        return redirect('dashboard')
    
    bulletins = Bulletin.objects.all().order_by('-created_at')
    return render(request, 'college_app/manage_bulletins.html', {'bulletins': bulletins})


@login_required
def create_bulletin(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can create bulletins')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        Bulletin.objects.create(
            title=title,
            content=content,
            image=image,
            posted_by=request.user
        )
        
        messages.success(request, 'Bulletin created successfully')
        return redirect('manage_bulletins')
    
    return render(request, 'college_app/create_bulletin.html')


@login_required
def edit_bulletin(request, bulletin_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can edit bulletins')
        return redirect('dashboard')
    
    bulletin = get_object_or_404(Bulletin, id=bulletin_id)
    
    if request.method == 'POST':
        bulletin.title = request.POST.get('title')
        bulletin.content = request.POST.get('content')
        image = request.FILES.get('image')
        if image:
            bulletin.image = image
        bulletin.save()
        
        messages.success(request, 'Bulletin updated successfully')
        return redirect('manage_bulletins')
    
    return render(request, 'college_app/edit_bulletin.html', {'bulletin': bulletin})


@login_required
def delete_bulletin(request, bulletin_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can delete bulletins')
        return redirect('dashboard')
    
    bulletin = get_object_or_404(Bulletin, id=bulletin_id)
    bulletin.delete()
    messages.success(request, 'Bulletin deleted successfully')
    return redirect('manage_bulletins')


@login_required
def view_bus_tracker(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can view bus tracker')
        return redirect('dashboard')
    
    bus_routes = BusRoute.objects.all()
    bus_locations = {}
    for route in bus_routes:
        latest_location = BusLocation.objects.filter(bus_route=route).order_by('-updated_at').first()
        bus_locations[route.id] = latest_location
    
    context = {
        'bus_routes': bus_routes,
        'bus_locations': bus_locations,
    }
    return render(request, 'college_app/view_bus_tracker.html', context)


@login_required
def view_assignments(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can view assignments')
        return redirect('dashboard')
    
    assignments = Assignment.objects.filter(is_active=True).order_by('-due_date')
    student_submissions = Submission.objects.filter(student=request.user)
    submitted_assignment_ids = student_submissions.values_list('assignment_id', flat=True)
    
    context = {
        'assignments': assignments,
        'submitted_assignment_ids': submitted_assignment_ids,
        'student_submissions': student_submissions,
    }
    return render(request, 'college_app/view_assignments.html', context)


@login_required
def submit_assignment(request, assignment_id):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can submit assignments')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if Submission.objects.filter(student=request.user, assignment=assignment).exists():
        messages.error(request, 'You have already submitted this assignment')
        return redirect('view_assignments')
    
    if request.method == 'POST':
        file = request.FILES.get('file')
        comments = request.POST.get('comments', '')
        
        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            file=file,
            comments=comments
        )
        
        messages.success(request, 'Assignment submitted successfully')
        return redirect('view_assignments')
    
    return render(request, 'college_app/submit_assignment.html', {'assignment': assignment})


@login_required
def create_assignment(request):
    if request.user.profile.role != 'teacher':
        messages.error(request, 'Only teachers can create assignments')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks')
        file = request.FILES.get('file')
        
        Assignment.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            max_marks=max_marks,
            created_by=request.user,
            file=file
        )
        
        messages.success(request, 'Assignment created successfully')
        return redirect('view_teacher_assignments')
    
    return render(request, 'college_app/create_assignment.html')


@login_required
def view_teacher_assignments(request):
    if request.user.profile.role != 'teacher':
        messages.error(request, 'Only teachers can view this page')
        return redirect('dashboard')
    
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')
    
    assignment_stats = []
    for assignment in assignments:
        total_students = User.objects.filter(profile__role='student').count()
        submissions = Submission.objects.filter(assignment=assignment)
        submitted_count = submissions.count()
        graded_count = submissions.filter(marks_obtained__isnull=False).count()
        
        assignment_stats.append({
            'assignment': assignment,
            'total_students': total_students,
            'submitted_count': submitted_count,
            'graded_count': graded_count,
        })
    
    return render(request, 'college_app/view_teacher_assignments.html', {'assignment_stats': assignment_stats})


@login_required
def grade_assignment(request, submission_id):
    if request.user.profile.role != 'teacher':
        messages.error(request, 'Only teachers can grade assignments')
        return redirect('dashboard')
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if submission.assignment.created_by != request.user:
        messages.error(request, 'You can only grade assignments you created')
        return redirect('view_teacher_assignments')
    
    if request.method == 'POST':
        marks_obtained = request.POST.get('marks_obtained')
        teacher_feedback = request.POST.get('teacher_feedback', '')
        
        submission.marks_obtained = marks_obtained
        submission.teacher_feedback = teacher_feedback
        submission.graded_at = timezone.now()
        submission.save()
        
        messages.success(request, 'Assignment graded successfully')
        return redirect('view_teacher_assignments')
    
    return render(request, 'college_app/grade_assignment.html', {'submission': submission})


@login_required
def view_assignment_submissions(request, assignment_id):
    if request.user.profile.role != 'teacher':
        messages.error(request, 'Only teachers can view submissions')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.created_by != request.user:
        messages.error(request, 'You can only view submissions for assignments you created')
        return redirect('view_teacher_assignments')
    
    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'college_app/view_assignment_submissions.html', context)
