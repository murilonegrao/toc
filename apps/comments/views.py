from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comment
from apps.tickets.models import Ticket


@login_required
def add_comment(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        from apps.tickets import services
        visible = services.get_tickets_for_user(request.user)
        if not visible.filter(id=ticket_id).exists():
            return redirect('/')
        content = request.POST.get('content', '').strip()
        internal = request.POST.get('internal') == 'on'

        if not content:
            messages.error(request, 'O comentário não pode estar vazio.')
            return redirect('tickets:detail', ticket_id=ticket_id)

        if internal and request.user.role not in ('admin', 'atendente'):
            internal = False

        Comment.objects.create(
            ticket=ticket,
            author=request.user,
            comment=content,
            internal=internal,
        )
        messages.success(request, 'Comentário adicionado.')

    return redirect('tickets:detail', ticket_id=ticket_id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    ticket_id = comment.ticket.id

    if request.user.role == 'admin':
        comment.delete()
        messages.success(request, 'Comentário removido.')
    else:
        messages.error(request, 'Sem permissão para remover este comentário.')

    return redirect('tickets:detail', ticket_id=ticket_id)
