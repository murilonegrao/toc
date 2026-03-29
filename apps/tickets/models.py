from django.db import models
from django.conf import settings

# Create your models here.

class Ticket(models.Model):
    
    class Type(models.TextChoices):
        SYSTEM = 'ORQUESTRADOR', 'Orquestrador'
        AUTOMATION = 'AUTOMACAO', 'Automacao'
        
    class Subtype(models.TextChoices):
        BUG_CORRECTION = 'correcao_bug', 'Correção'
        IMPROVEMENT = 'melhoria', 'Melhoria'
        NEW_FEATURE = 'nova_funcionalidade', 'Nova Funcionalidade'
        ATTUALIZATION = 'atualizacao', 'Atualização'
        NEW = 'novo', 'Novo'
        
    class Status(models.TextChoices):
        OPEN = 'aberto', 'Aberto'
        RECEIVED = 'recebido', 'Recebido'
        IN_PROGRESS = 'em_desenvolvimento', 'Em Desenvolvimento'
        IN_PRODUCTION = 'em_producao', 'Em Produção'
        WAITING_FOR_CLIENT = 'aguardando_cliente', 'Aguardando Cliente'
        NOT_ATTENDED = 'nao_atendido', 'Não Atendido'
        CLOSED = 'fechado', 'Fechado'
        CANCELLED = 'cancelado', 'Cancelado'
        
    class Priority(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        HIGH = 'alta', 'Alta'
        URGENT = 'urgente', 'Urgente'
        
    protocol = models.PositiveIntegerField(unique=True, null=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=Type.choices)
    subtype = models.CharField(max_length=20, choices=Subtype.choices, default=Subtype.BUG_CORRECTION)
    subject = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    url_system = models.URLField(null=True, blank=True)
    steps = models.TextField(null=True, blank=True)
    normal_behavior = models.TextField(null=True, blank=True)
    unexpected_behavior = models.TextField(null=True, blank=True)
    justification = models.TextField(null=True, blank=True)
    acceptance_criteria = models.TextField(null=True, blank=True)
    manual_process = models.TextField(null=True, blank=True)
    automation_name = models.CharField(max_length=255, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, null=False, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, null=False, default=Status.OPEN)
    notify_by_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'#{self.protocol} - {self.subject}'
    
class TicketStatusLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=25, choices=Ticket.Status.choices)
    new_status = models.CharField(max_length=25, choices=Ticket.Status.choices)
    justification = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    