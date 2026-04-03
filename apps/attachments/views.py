from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Attachment
from apps.tickets.models import Ticket
import uuid
import os
import unicodedata
from apps.tickets import services
import re

ALLOWED_EXTENSIONS = {
    '.pdf', '.png', '.jpg', '.jpeg', '.gif', 
    '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv'
}

@login_required
def upload_attachment(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        visible = services.get_tickets_for_user(request.user)
        if not visible.filter(id=ticket_id).exists():
            return redirect('/')
            
        file = request.FILES.get('file')

        if not file:
            messages.error(request, 'Nenhum arquivo selecionado.')
            return redirect('tickets:detail', ticket_id=ticket_id)
            
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            messages.error(request, f'Tipo de arquivo não permitido ({ext}).')
            return redirect('tickets:detail', ticket_id=ticket_id)

        if file.size > 10 * 1024 * 1024:
            messages.error(request, 'O arquivo excede o tamanho máximo de 10MB.')
            return redirect('tickets:detail', ticket_id=ticket_id)

        file.name = normalize_filename(file.name)

        Attachment.objects.create(
            ticket=ticket,
            author=request.user,
            file=file,
            original_name=file.name,
            size=file.size,
            mime_type=file.content_type,
        )

        messages.success(request, f'Arquivo {file.name} enviado com sucesso.')
        return redirect('tickets:detail', ticket_id=ticket_id)
        

def normalize_filename(filename):
    #remove acentos
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    #mantém só letras, números, pontos e hífens
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\-]', '_', name)
    #adiciona uuid para evitar colisão
    return f'{name}_{uuid.uuid4().hex[:8]}{ext.lower()}'