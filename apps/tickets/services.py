from django.db import transaction, models
from .models import Ticket, TicketStatusLog
from apps.accounts.models import UserDepartment
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()

TRANSITIONS = {
    'aberto': ['recebido'],
    'recebido': ['em_desenvolvimento', 'nao_atendido', 'cancelado'],
    'em_desenvolvimento': ['em_producao', 'nao_atendido', 'cancelado'],
    'em_producao': ['aguardando_cliente', 'cancelado'],
    'aguardando_cliente': ['fechado', 'em_desenvolvimento', 'cancelado'],
}


def change_ticket_status(ticket, new_status, user, justification=None):
    with transaction.atomic():
        
        #pega o valor atual do status como old_status
        old_status = ticket.status
        
        #verifica se a transição é válida
        if new_status not in TRANSITIONS.get(old_status, []):
            raise ValueError(f'Transição inválida de {old_status} para {new_status}')
        
        if new_status == Ticket.Status.NOT_ATTENDED and not justification:
            raise ValueError('Justificativa obrigatória para marcar como Não Atendido.')
        
        if new_status == 'em_desenvolvimento' and not ticket.development_started_at:
            ticket.development_started_at = timezone.now()
        #cria o log de status
        TicketStatusLog.objects.create(
            ticket=ticket,
            changed_by=user,
            old_status=old_status,
            new_status=new_status,
            justification=justification
        )
        #atualiza o status
        ticket.status = new_status
        ticket.save()


def generate_ticket_protocol():
    with transaction.atomic():
        last = Ticket.objects.select_for_update().aggregate(max=models.Max('protocol'))
        return (last['max'] or 0) + 1


def get_tickets_for_user(user):
    if user.role in (User.Roles.ADMIN, User.Roles.ATENDENTE):
        return Ticket.objects.all()
    elif user.role == User.Roles.GESTOR_UNIDADE:
        user_departments = UserDepartment.objects.filter(user=user).values_list('department', flat=True)
        return Ticket.objects.filter(department__in=user_departments)
    elif user.role == User.Roles.CLIENTE:
        return Ticket.objects.filter(author=user)
    else:
        return Ticket.objects.none()
