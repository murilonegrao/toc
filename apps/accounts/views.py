from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserDepartment, User
from apps.departments.models import Department


def pending_approval(request):
    return render(request, 'accounts/pending.html')


def select_department(request):
    if request.method == 'GET':
        departments = Department.objects.filter(active=True)
        return render(request, 'accounts/select_department.html', {'departments': departments})
    elif request.method == 'POST':
        department = get_object_or_404(Department, id=request.POST.get('department'))
        UserDepartment.objects.get_or_create(user=request.user, department=department)
        return redirect('accounts:pending')


@login_required
def pending_users(request):
    if request.user.role not in ('admin', 'atendente', 'gestor_unidade'):
        return redirect('/')

    # Define pending primeiro
    pending = User.objects.filter(
        is_approved=False,
        is_active=True
    ).prefetch_related('userdepartment_set__department')

    # Depois filtra para gestor
    if request.user.role == 'gestor_unidade':
        my_depts = UserDepartment.objects.filter(
            user=request.user
        ).values_list('department_id', flat=True)

        pending = pending.filter(
            userdepartment__department_id__in=my_depts
        ).distinct()

    return render(request, 'accounts/pending_users.html', {
        'pending': pending,
        'is_gestor': request.user.role == 'gestor_unidade',
    })

@login_required
def approve_user(request, user_id):
    if request.user.role not in ('admin', 'atendente', 'gestor_unidade'):
        return redirect('/')

    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Só permite aprovar usuários pendentes
        if user.is_approved:
            messages.error(request, 'Este usuário já está aprovado.')
            return redirect('accounts:pending_users')

        if request.user.role == 'gestor_unidade':
            # Gestor só pode aprovar usuários do seu próprio departamento
            my_depts = UserDepartment.objects.filter(user=request.user).values_list('department_id', flat=True)
            if not user.userdepartment_set.filter(department_id__in=my_depts).exists():
                messages.error(request, 'Você não tem permissão para aprovar usuários fora de seus departamentos.')
                return redirect('accounts:pending_users')
            user.role = 'cliente'
        else:
            role = request.POST.get('role', 'cliente')
            if role in dict(User.Roles.choices):
                user.role = role
                
        user.is_approved = True
        user.is_active = True
        user.rejection_reason = ''
        user.save()
        messages.success(request, f'{user.name} aprovado com sucesso.')

    return redirect('accounts:pending_users')


@login_required
def reject_user(request, user_id):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        reason = request.POST.get('rejection_reason', '')
        user.rejection_reason = reason
        user.is_approved = False
        user.is_active = False  # desativa o acesso
        user.save()
        messages.warning(request, f'Cadastro de {user.name} rejeitado.')

    return redirect('accounts:pending_users')


@login_required
def user_list(request):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    # Usuários aprovados e ativos
    users = User.objects.filter(
        is_approved=True,
        is_active=True
    ).prefetch_related('userdepartment_set__department').order_by('name')

    # Usuários inativos/rejeitados
    inactive_users = User.objects.filter(
        is_active=False
    ).prefetch_related('userdepartment_set__department').order_by('name')

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'inactive_users': inactive_users,
    })

@login_required
def user_edit(request, user_id):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Atualiza papel
        role = request.POST.get('role')
        if role in dict(User.Roles.choices):
            user.role = role

        # Ativa ou inativa
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()

        # Atualiza departamentos
        UserDepartment.objects.filter(user=user).delete()
        dept_ids = request.POST.getlist('departments')
        for dept_id in dept_ids:
            dept = Department.objects.filter(id=dept_id).first()
            if dept:
                UserDepartment.objects.create(user=user, department=dept)

        messages.success(request, f'Usuário {user.name} atualizado com sucesso.')
        return redirect('accounts:user_list')

    departments = Department.objects.filter(active=True)
    user_dept_ids = list(
        UserDepartment.objects.filter(user=user).values_list('department_id', flat=True)
    )

    return render(request, 'accounts/user_edit.html', {
        'user_obj': user,
        'departments': departments,
        'user_dept_ids': user_dept_ids,
        'roles': User.Roles.choices,
    })