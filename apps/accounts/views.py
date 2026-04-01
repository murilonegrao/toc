from django.shortcuts import render

# Create your views here.
def pending_approval(request):
    return render(request, 'accounts/pending.html')

def select_department(request):
    return render(request, 'accounts/select_department.html')

