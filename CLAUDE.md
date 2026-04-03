# Contexto do Projeto — TOC

Este arquivo fornece contexto para IAs assistentes (Claude, Antigravity, etc.) trabalharem neste projeto.

---

## O que é o TOC

Sistema de gestão de chamados (tickets) desenvolvido para o Núcleo de Automação de Procedimentos do TJGO. Integrado visualmente ao Orquestrador DPE.

---

## Regras de arquitetura — LEIA ANTES DE ESCREVER CÓDIGO

### 1. Toda lógica de negócio fica em `services.py`

Views devem ser finas — só recebem request, chamam service, retornam response.

```python
# ❌ ERRADO — lógica na view
def change_status(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.status = request.POST.get('status')
    ticket.save()

# ✅ CORRETO — view chama service
def change_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    services.change_ticket_status(ticket, request.POST.get('status'), request.user)
    return redirect('tickets:detail', ticket_id=ticket_id)
```

### 2. FKs entre apps usam string lazy

```python
# ❌ ERRADO
from apps.tickets.models import Ticket
ticket = models.ForeignKey(Ticket, ...)

# ✅ CORRETO
ticket = models.ForeignKey('tickets.Ticket', ...)
```

### 3. Referência ao User model

```python
# ❌ ERRADO
from apps.accounts.models import User

# ✅ CORRETO entre apps
from django.conf import settings
author = models.ForeignKey(settings.AUTH_USER_MODEL, ...)

# ✅ CORRETO em services/views
from django.contrib.auth import get_user_model
User = get_user_model()
```

### 4. Sem lógica nos templates

Templates só renderizam dados. Lógica de filtro/permissão fica na view ou no service.

### 5. Comentários são imutáveis

Por decisão arquitetural, comentários não podem ser deletados — funcionam como log de auditoria permanente.

---

## Estrutura de apps

```
apps/accounts/     — User (AbstractUser, email login), UserDepartment, fluxo de aprovação
apps/attachments/  — Upload de arquivos para MinIO/S3
apps/comments/     — Comentários nos tickets (imutáveis)
apps/core/         — Dashboard, views genéricas
apps/departments/  — Department (name, initials, color, active)
apps/notifications/ — NotificationLog (sem envio implementado ainda)
apps/tickets/      — Ticket, TicketStatusLog, TicketService, VisibilityService
```

---

## Modelos importantes

### User
```python
# campos extras além do AbstractUser
email          # USERNAME_FIELD
name           # CharField obrigatório
phone          # CharField opcional
role           # TextChoices: admin, atendente, gestor_unidade, cliente
is_approved    # BooleanField — controla acesso ao sistema
rejection_reason # TextField opcional
```

### Ticket
```python
protocol       # IntegerField único — gerado via MAX+1 com select_for_update
author         # FK para User
department     # FK para Department
type           # TextChoices: ORQUESTRADOR, AUTOMACAO
subtype        # TextChoices: correcao_bug, melhoria, nova_funcionalidade, etc
status         # TextChoices — controlado pela máquina de estados
priority       # TextChoices: normal, alta, urgente
# campos condicionais (null=True) para cada tipo de chamado
```

### Máquina de estados

```python
TRANSITIONS = {
    'aberto': ['recebido'],
    'recebido': ['em_desenvolvimento', 'nao_atendido', 'cancelado'],
    'em_desenvolvimento': ['em_producao', 'nao_atendido', 'cancelado'],
    'em_producao': ['aguardando_cliente', 'cancelado'],
    'aguardando_cliente': ['finalizado', 'em_desenvolvimento', 'cancelado'],
}
```

---

## Visibilidade de tickets

```python
# apps/tickets/services.py — get_tickets_for_user()
admin, atendente  → Ticket.objects.all()
gestor_unidade    → filtra por departamentos do usuário
cliente           → filtra por autor
```

---

## Middleware de aprovação

`apps/accounts/middleware.py` — intercepta todas as requisições:
- URLs isentas: login, logout, signup, pending, select-department, admin
- admin → passa direto
- atendente → precisa de is_approved=True
- gestor/cliente → precisa de UserDepartment + is_approved=True

---

## Storage

Arquivos vão para MinIO (dev) ou S3 (produção) via `django-storages`.
Configuração via variáveis de ambiente — zero mudança de código entre ambientes.

Nomes de arquivo são normalizados antes do upload:
- Remove acentos e caracteres especiais
- Adiciona UUID de 8 chars para evitar colisão

---

## CSS

Um único arquivo `static/css/main.css` — sem CSS inline nos templates (exceto valores dinâmicos como cores de departamento).

Paleta fiel ao Orquestrador DPE:
- Sidebar: `#282f3a`
- Header do usuário: `#1a1f26`
- Accent: `#F4645F`
- Conteúdo principal: `#f4f6f8` (claro)

---

## Convenções

- Idioma da interface: pt-BR
- Commits: Conventional Commits em inglês
- Sem DRF, sem React, sem Vue — Django Templates + HTMX
- PostgreSQL obrigatório — sem SQLite
- Settings split: base / development / production
- Secrets via django-environ — nunca hardcoded