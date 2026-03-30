from django.shortcuts import redirect
from django.urls import reverse
from apps.accounts.models import User, UserDepartment


class ApprovalRequiredMiddleware:

    EXEMPT_URLS = [
        '/accounts/login/',
        '/accounts/signup/',
        '/accounts/pending/',
        '/accounts/select-department/',
        '/admin/',
    ]
        
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.EXEMPT_URLS:
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.user.is_authenticated:
            if request.user.role == User.Roles.ADMIN:
                return self.get_response(request)
            elif request.user.role == User.Roles.ATENDENTE:
                if request.user.is_approved:
                    return self.get_response(request)
                else:
                    return redirect('accounts:pending')
            elif request.user.role in (User.Roles.GESTOR_UNIDADE, User.Roles.CLIENTE):
                if not UserDepartment.objects.filter(user=request.user).exists():
                    return redirect('accounts:select-department')
                elif not request.user.is_approved:
                    return redirect('accounts:pending')
                else:
                    return self.get_response(request)
        
        response = self.get_response(request)
        return response
        