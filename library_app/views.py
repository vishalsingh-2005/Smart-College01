from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from .models import Document

@login_required
def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        if file:
            Document.objects.create(
                title=title,
                description=description,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, 'Document uploaded successfully!')
            return redirect('list_documents')
        else:
            messages.error(request, 'Please select a file to upload')
    
    return render(request, 'library_app/upload.html')

@login_required
def list_documents(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'library_app/list.html', {'documents': documents})

@login_required
def download_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    try:
        return FileResponse(document.file.open('rb'), as_attachment=True, filename=document.file.name)
    except FileNotFoundError:
        raise Http404("File not found")
