from django.db import transaction, models
from .models import Ticket, TicketStatusLog


def change_ticket_status(ticket, new_status, user, justification=None):

    TRANSITIONS = {
        'aberto': ['recebido'],
        'recebido': ['em_desenvolvimento', 'nao_atendido', 'cancelado'],
        'em_desenvolvimento': ['em_producao', 'nao_atendido', 'cancelado'],
        'em_producao': ['aguardando_cliente', 'cancelado'],
        'aguardando_cliente': ['finalizado', 'em_desenvolvimento', 'cancelado'],        
    }

    with transaction.atomic():
        
        #pega o valor atual do status como old_status
        old_status = ticket.status
        
        #verifica se a transição é válida
        if new_status not in TRANSITIONS.get(old_status, []):
            raise ValueError(f'Invalid status transition from {old_status} to {new_status}')
        
        if new_status == Ticket.Status.NOT_ATTENDED and not justification:
            raise ValueError('Justification is required when changing status to NOT_ATTENDED')
        
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

