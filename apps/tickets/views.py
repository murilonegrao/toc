import json
import os

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Ticket
from .forms import TicketForm
from . import services
from apps.comments.models import Comment
from apps.attachments.models import Attachment
from apps.attachments.views import normalize_filename, ALLOWED_EXTENSIONS
from apps.accounts.models import UserDepartment, User


@login_required
def ticket_list(request):
    tickets = services.get_tickets_for_user(request.user)

    dept_id = request.GET.get('dept')
    if dept_id:
        tickets = tickets.filter(department_id=dept_id)

    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)

    tickets = tickets.select_related('author', 'department').order_by('-created_at')

    return render(request, 'tickets/list.html', {
        'tickets': tickets,
        'status_choices': Ticket.Status.choices,
        'current_status': status,
    })


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    visible = services.get_tickets_for_user(request.user)
    if not visible.filter(id=ticket_id).exists():
        return redirect('/')

    logs = ticket.ticketstatuslog_set.select_related('changed_by').order_by('-created_at')

    comments = Comment.objects.filter(ticket=ticket).select_related('author').order_by('created_at')
    if request.user.role not in ('admin', 'atendente'):
        comments = comments.filter(internal=False)

    attachments = Attachment.objects.filter(ticket=ticket).select_related('author').order_by('created_at')

    # Atendentes disponíveis para atribuição
    atendentes = User.objects.filter(
        role__in=['admin', 'atendente'],
        is_active=True,
        is_approved=True,
    )

    # Verifica se o usuário pode ver o card de mudar status em aguardando_cliente
    is_gestor_da_unidade = (
        request.user.role == 'gestor_unidade' and
        UserDepartment.objects.filter(
            user=request.user,
            department=ticket.department
        ).exists()
    )

    pode_responder = (
        request.user.role in ('admin', 'atendente') or
        request.user == ticket.author or
        is_gestor_da_unidade
    )

    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'logs': logs,
        'comments': comments,
        'attachments': attachments,
        'transitions': services.TRANSITIONS.get(ticket.status, []),
        'status_choices': Ticket.Status.choices,
        'atendentes': atendentes,
        'pode_responder': pode_responder,
        'is_gestor_da_unidade': is_gestor_da_unidade,
    })


@login_required
def ticket_create(request):
    if request.method == 'GET':
        form = TicketForm(user=request.user)
        return render(request, 'tickets/create.html', {'form': form})

    elif request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            ticket.protocol = services.generate_ticket_protocol()
            ticket.status = Ticket.Status.OPEN
            ticket.save()

            files = request.FILES.getlist('attachments')
            for file in files:
                if file.size <= 10 * 1024 * 1024:
                    ext = os.path.splitext(file.name)[1].lower()
                    if ext in ALLOWED_EXTENSIONS:
                        file.name = normalize_filename(file.name)
                        Attachment.objects.create(
                            ticket=ticket,
                            author=request.user,
                            file=file,
                            original_name=file.name,
                            size=file.size,
                            mime_type=file.content_type,
                        )

            messages.success(request, f'Chamado #{ticket.protocol} aberto com sucesso.')
            return redirect('tickets:detail', ticket_id=ticket.id)

        return render(request, 'tickets/create.html', {'form': form})


@login_required
def ticket_change_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)

        visible = services.get_tickets_for_user(request.user)
        if not visible.filter(id=ticket_id).exists():
            return redirect('/')

        # Verifica permissão para a transição
        is_gestor_da_unidade = (
            request.user.role == 'gestor_unidade' and
            UserDepartment.objects.filter(
                user=request.user,
                department=ticket.department
            ).exists()
        )

        can_change_status = (
            request.user.role in ('admin', 'atendente') or
            (
                ticket.status == 'aguardando_cliente' and
                (request.user == ticket.author or is_gestor_da_unidade)
            )
        )

        if not can_change_status:
            messages.error(request, 'Sem permissão para alterar o status deste chamado.')
            return redirect('tickets:detail', ticket_id=ticket_id)

        new_status = request.POST.get('new_status')
        justification = request.POST.get('justification', '')

        try:
            services.change_ticket_status(
                ticket=ticket,
                new_status=new_status,
                user=request.user,
                justification=justification,
            )

            # Atualiza atendentes responsáveis
            assignees = request.POST.getlist('assignees')
            if assignees:
                ticket.assignees.set(assignees)

            # Atualiza prazo estimado
            estimated_days = request.POST.get('estimated_days')
            if estimated_days:
                ticket.estimated_days = int(estimated_days)
                ticket.save()

            messages.success(request, 'Status atualizado com sucesso.')
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('tickets:detail', ticket_id=ticket_id)


@login_required
def ticket_kanban(request):
    if request.user.role not in ('admin', 'atendente'):
        messages.error(request, 'Você não tem permissão para acessar o kanban.')
        return redirect('tickets:list')

    tickets = Ticket.objects.all().select_related('author', 'department').order_by('-created_at')

    kanban = {}
    for status, label in Ticket.Status.choices:
        kanban[status] = {
            'label': label,
            'tickets': tickets.filter(status=status)
        }

    return render(request, 'tickets/kanban.html', {
        'kanban': kanban,
        'transitions_json': json.dumps(services.TRANSITIONS),
    })


@login_required
@require_POST
def kanban_move_ticket(request, ticket_id):
    if request.user.role not in ('admin', 'atendente'):
        return JsonResponse({'ok': False, 'error': 'Sem permissão.'}, status=403)

    ticket = get_object_or_404(Ticket, id=ticket_id)
    new_status = request.POST.get('new_status', '')
    justification = request.POST.get('justification', '')

    try:
        services.change_ticket_status(
            ticket=ticket,
            new_status=new_status,
            user=request.user,
            justification=justification,
        )
        return JsonResponse({'ok': True})
    except ValueError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
def my_tickets(request):
    if request.user.role == 'admin':
        tickets = Ticket.objects.filter(
            author__role__in=('admin', 'atendente')
        )
    elif request.user.role == 'atendente':
        tickets = Ticket.objects.filter(author=request.user)
    elif request.user.role == 'gestor_unidade':
        user_departments = UserDepartment.objects.filter(
            user=request.user
        ).values_list('department', flat=True)
        tickets = Ticket.objects.filter(
            Q(department__in=user_departments) | Q(author=request.user)
        )
    else:
        tickets = Ticket.objects.filter(author=request.user)

    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)

    tickets = tickets.select_related('author', 'department').order_by('-created_at')

    return render(request, 'tickets/my_tickets.html', {
        'tickets': tickets,
        'status_choices': Ticket.Status.choices,
        'current_status': status,
        'page_title': 'Meus Chamados',
    })