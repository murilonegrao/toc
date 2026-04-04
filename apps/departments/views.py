from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department


@login_required
def department_list(request):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    departments = Department.objects.all().order_by('name')
    return render(request, 'departments/list.html', {'departments': departments})


@login_required
def department_create(request):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        initials = request.POST.get('initials', '').strip().upper()
        color = request.POST.get('color', '#F4645F')
        active = request.POST.get('active') == 'on'

        if not name or not initials:
            messages.error(request, 'Nome e sigla são obrigatórios.')
            return redirect('departments:create')

        if Department.objects.filter(initials=initials).exists():
            messages.error(request, f'Já existe um departamento com a sigla {initials}.')
            return redirect('departments:create')

        Department.objects.create(
            name=name,
            initials=initials,
            color=color,
            active=active,
        )
        messages.success(request, f'Departamento {name} criado com sucesso.')
        return redirect('departments:list')

    return render(request, 'departments/form.html', {'action': 'Criar'})


@login_required
def department_edit(request, dept_id):
    if request.user.role not in ('admin', 'atendente'):
        return redirect('/')

    dept = get_object_or_404(Department, id=dept_id)

    if request.method == 'POST':
        dept.name = request.POST.get('name', '').strip()
        dept.initials = request.POST.get('initials', '').strip().upper()
        dept.color = request.POST.get('color', '#F4645F')
        dept.active = request.POST.get('active') == 'on'

        if Department.objects.filter(initials=dept.initials).exclude(id=dept.id).exists():
            messages.error(request, f'Já existe um departamento com a sigla {dept.initials}.')
            return redirect('departments:edit', dept_id=dept.id)

        dept.save()
        messages.success(request, f'Departamento {dept.name} atualizado.')
        return redirect('departments:list')

    return render(request, 'departments/form.html', {
        'action': 'Editar',
        'dept': dept,
    })