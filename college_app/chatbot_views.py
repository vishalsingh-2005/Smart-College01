from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import CollegeInfo


@login_required
def manage_colleges(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can manage college data')
        return redirect('dashboard')
    
    colleges = CollegeInfo.objects.all()
    return render(request, 'college_app/manage_colleges.html', {'colleges': colleges})


@login_required
def create_college(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can create college data')
        return redirect('dashboard')
    
    if request.method == 'POST':
        CollegeInfo.objects.create(
            name=request.POST.get('name'),
            location=request.POST.get('location'),
            established_year=request.POST.get('established_year') or None,
            college_type=request.POST.get('college_type'),
            placement_percentage=request.POST.get('placement_percentage') or None,
            avg_package=request.POST.get('avg_package') or None,
            highest_package=request.POST.get('highest_package') or None,
            hostel_fees=request.POST.get('hostel_fees') or None,
            tuition_fees=request.POST.get('tuition_fees') or None,
            admission_process=request.POST.get('admission_process'),
            courses_offered=request.POST.get('courses_offered'),
            facilities=request.POST.get('facilities'),
            contact_email=request.POST.get('contact_email'),
            contact_phone=request.POST.get('contact_phone'),
            website=request.POST.get('website'),
        )
        messages.success(request, 'College information added successfully')
        return redirect('manage_colleges')
    
    return render(request, 'college_app/create_college.html')


@login_required
def edit_college(request, college_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can edit college data')
        return redirect('dashboard')
    
    college = get_object_or_404(CollegeInfo, id=college_id)
    
    if request.method == 'POST':
        college.name = request.POST.get('name')
        college.location = request.POST.get('location')
        college.established_year = request.POST.get('established_year') or None
        college.college_type = request.POST.get('college_type')
        college.placement_percentage = request.POST.get('placement_percentage') or None
        college.avg_package = request.POST.get('avg_package') or None
        college.highest_package = request.POST.get('highest_package') or None
        college.hostel_fees = request.POST.get('hostel_fees') or None
        college.tuition_fees = request.POST.get('tuition_fees') or None
        college.admission_process = request.POST.get('admission_process')
        college.courses_offered = request.POST.get('courses_offered')
        college.facilities = request.POST.get('facilities')
        college.contact_email = request.POST.get('contact_email')
        college.contact_phone = request.POST.get('contact_phone')
        college.website = request.POST.get('website')
        college.save()
        
        messages.success(request, 'College information updated successfully')
        return redirect('manage_colleges')
    
    return render(request, 'college_app/edit_college.html', {'college': college})


@login_required
def delete_college(request, college_id):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Only admins can delete college data')
        return redirect('dashboard')
    
    college = get_object_or_404(CollegeInfo, id=college_id)
    college.delete()
    messages.success(request, 'College information deleted successfully')
    return redirect('manage_colleges')


def chatbot_query(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip().lower()
        
        if not query:
            return JsonResponse({'error': 'Please enter a query'}, status=400)
        
        colleges = CollegeInfo.objects.all()
        results = []
        
        for college in colleges:
            if query in college.name.lower():
                response = f"<strong>{college.name}</strong><br>"
                response += f"📍 Location: {college.location}<br>"
                
                if college.placement_percentage:
                    response += f"📊 Placement Rate: {college.placement_percentage}%<br>"
                if college.avg_package:
                    response += f"💰 Average Package: ${college.avg_package}<br>"
                if college.highest_package:
                    response += f"🏆 Highest Package: ${college.highest_package}<br>"
                if college.hostel_fees:
                    response += f"🏠 Hostel Fees: ${college.hostel_fees}/year<br>"
                if college.tuition_fees:
                    response += f"📚 Tuition Fees: ${college.tuition_fees}/year<br>"
                if college.admission_process:
                    response += f"📝 Admission: {college.admission_process[:200]}<br>"
                if college.website:
                    response += f"🌐 Website: <a href='{college.website}' target='_blank'>{college.website}</a><br>"
                
                results.append(response)
        
        if results:
            return JsonResponse({'response': '<br><br>'.join(results)})
        else:
            return JsonResponse({
                'response': '❌ Details not available for this college. Please contact admin to add information.'
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
