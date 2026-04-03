import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User, UserDepartment
from apps.departments.models import Department
from apps.tickets.models import Ticket, TicketStatusLog
from apps.comments.models import Comment


class Command(BaseCommand):
    help = 'Popula o banco com dados de teste'

    def handle(self, *args, **options):
        self.stdout.write('Criando departamentos...')
        departments = self._create_departments()

        self.stdout.write('Criando usuários...')
        users = self._create_users(departments)

        self.stdout.write('Criando tickets...')
        tickets = self._create_tickets(users, departments)

        self.stdout.write('Criando comentários...')
        self._create_comments(tickets, users)

        self.stdout.write('Criando logs de status...')
        self._create_status_logs(tickets, users)

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed concluído!'
            f'\n  {len(departments)} departamentos'
            f'\n  {len(users)} usuários'
            f'\n  {len(tickets)} tickets'
        ))

    def _create_departments(self):
        dept_data = [
            {'name': 'Tecnologia da Informação', 'initials': 'TI', 'color': '#3B82F6'},
            {'name': 'Recursos Humanos', 'initials': 'RH', 'color': '#10B981'},
            {'name': 'Financeiro', 'initials': 'FIN', 'color': '#F59E0B'},
            {'name': 'Comercial', 'initials': 'COM', 'color': '#EF4444'},
            {'name': 'Operações', 'initials': 'OPS', 'color': '#8B5CF6'},
            {'name': 'Jurídico', 'initials': 'JUR', 'color': '#6366F1'},
        ]
        departments = []
        for d in dept_data:
            dept, created = Department.objects.get_or_create(
                initials=d['initials'],
                defaults=d,
            )
            departments.append(dept)
            status = 'criado' if created else 'já existia'
            self.stdout.write(f'  [{status}] {dept.name}')
        return departments

    def _create_users(self, departments):
        user_data = [
            # Admins
            {
                'email': 'admin@toc.com',
                'name': 'Carlos Administrador',
                'role': 'admin',
                'phone': '(11) 99999-0001',
            },
            # Atendentes
            {
                'email': 'maria.atendente@toc.com',
                'name': 'Maria Oliveira',
                'role': 'atendente',
                'phone': '(11) 99999-0002',
            },
            {
                'email': 'joao.atendente@toc.com',
                'name': 'João Santos',
                'role': 'atendente',
                'phone': '(11) 99999-0003',
            },
            # Gestores
            {
                'email': 'ana.gestora@toc.com',
                'name': 'Ana Costa',
                'role': 'gestor_unidade',
                'phone': '(21) 99999-0004',
                'departments': ['TI', 'OPS'],
            },
            {
                'email': 'pedro.gestor@toc.com',
                'name': 'Pedro Almeida',
                'role': 'gestor_unidade',
                'phone': '(21) 99999-0005',
                'departments': ['RH', 'FIN'],
            },
            # Clientes
            {
                'email': 'lucas.cliente@empresa.com',
                'name': 'Lucas Ferreira',
                'role': 'cliente',
                'phone': '(31) 99999-0006',
                'departments': ['TI'],
            },
            {
                'email': 'julia.cliente@empresa.com',
                'name': 'Júlia Rodrigues',
                'role': 'cliente',
                'phone': '(31) 99999-0007',
                'departments': ['RH', 'FIN'],
            },
            {
                'email': 'rafael.cliente@empresa.com',
                'name': 'Rafael Nascimento',
                'role': 'cliente',
                'phone': '(41) 99999-0008',
                'departments': ['COM'],
            },
            {
                'email': 'camila.cliente@empresa.com',
                'name': 'Camila Barbosa',
                'role': 'cliente',
                'phone': '(41) 99999-0009',
                'departments': ['TI', 'OPS'],
            },
            {
                'email': 'fernanda.cliente@empresa.com',
                'name': 'Fernanda Lima',
                'role': 'cliente',
                'phone': '(51) 99999-0010',
                'departments': ['JUR', 'FIN'],
            },
        ]

        dept_map = {d.initials: d for d in departments}
        users = []

        for u in user_data:
            dept_initials = u.pop('departments', [])
            user, created = User.objects.get_or_create(
                email=u['email'],
                defaults={
                    **u,
                    'is_approved': True,
                    'is_active': True,
                },
            )
            if created:
                user.set_password('toc12345')
                user.save()

            # Atribui departamentos
            for initials in dept_initials:
                dept = dept_map.get(initials)
                if dept:
                    UserDepartment.objects.get_or_create(user=user, department=dept)

            users.append(user)
            status = 'criado' if created else 'já existia'
            self.stdout.write(f'  [{status}] {user.name} ({user.role})')

        return users

    def _create_tickets(self, users, departments):
        # Pega apenas clientes e gestores como autores de tickets
        authors = [u for u in users if u.role in ('cliente', 'gestor_unidade')]

        ticket_data = [
            # Tickets de TI
            {
                'subject': 'Erro ao gerar relatório de vendas',
                'description': 'O sistema apresenta erro 500 ao tentar gerar o relatório mensal de vendas. O erro ocorre sempre que o período selecionado é superior a 3 meses.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'urgente',
                'status': 'em_desenvolvimento',
                'dept_initials': 'TI',
                'steps': '1. Acessar menu Relatórios\n2. Selecionar "Vendas Mensal"\n3. Escolher período > 3 meses\n4. Clicar em Gerar',
                'unexpected_behavior': 'Tela fica branca e retorna erro 500.',
                'normal_behavior': 'O relatório deveria ser gerado em PDF.',
            },
            {
                'subject': 'Implementar login com autenticação 2FA',
                'description': 'Necessidade de implementar autenticação de dois fatores para aumentar a segurança do sistema.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'alta',
                'status': 'recebido',
                'dept_initials': 'TI',
                'acceptance_criteria': '- Usuário deve poder ativar 2FA via app\n- SMS como fallback\n- QR Code para configuração',
            },
            {
                'subject': 'Lentidão no módulo de cadastro',
                'description': 'O módulo de cadastro de produtos está extremamente lento, demorando mais de 30 segundos para salvar.',
                'type': 'ORQUESTRADOR',
                'subtype': 'melhoria',
                'priority': 'alta',
                'status': 'aberto',
                'dept_initials': 'TI',
                'url_system': 'https://sistema.empresa.com/cadastro/produtos',
            },
            {
                'subject': 'Atualizar versão do framework para v5.0',
                'description': 'O framework atual está na versão 3.2 e precisa ser atualizado para a 5.0 para suporte a novas funcionalidades.',
                'type': 'ORQUESTRADOR',
                'subtype': 'atualizacao',
                'priority': 'normal',
                'status': 'em_producao',
                'dept_initials': 'TI',
            },
            {
                'subject': 'Botão de exportar CSV não funciona no Safari',
                'description': 'Ao utilizar o navegador Safari, o botão de exportar dados para CSV não responde ao clique.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'normal',
                'status': 'aguardando_cliente',
                'dept_initials': 'TI',
                'steps': '1. Abrir o Safari\n2. Navegar até Relatórios > Exportar\n3. Clicar em "Exportar CSV"',
                'unexpected_behavior': 'Nada acontece ao clicar no botão.',
                'normal_behavior': 'Deveria iniciar o download do arquivo CSV.',
            },
            # Tickets de RH
            {
                'subject': 'Erro no cálculo de férias',
                'description': 'O sistema está calculando incorretamente o período de férias para funcionários com mais de 10 anos de empresa.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'urgente',
                'status': 'em_desenvolvimento',
                'dept_initials': 'RH',
            },
            {
                'subject': 'Novo relatório de absenteísmo',
                'description': 'Criar um relatório que mostre o índice de absenteísmo por departamento, com gráficos comparativos mês a mês.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'normal',
                'status': 'aberto',
                'dept_initials': 'RH',
                'acceptance_criteria': '- Filtro por período\n- Gráfico de barras comparativo\n- Exportar para PDF e Excel',
            },
            {
                'subject': 'Integração com novo sistema de ponto',
                'description': 'Precisamos integrar o sistema atual com o novo relógio de ponto digital da marca XYZ.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'alta',
                'status': 'recebido',
                'dept_initials': 'RH',
            },
            # Tickets Financeiro
            {
                'subject': 'Divergência no fechamento contábil',
                'description': 'Os valores do fechamento contábil de março não batem com os extratos bancários. Diferença de R$ 15.432,00.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'urgente',
                'status': 'em_desenvolvimento',
                'dept_initials': 'FIN',
            },
            {
                'subject': 'Automatizar conciliação bancária',
                'description': 'Processo de conciliação bancária é manual e leva 2 dias. Precisa ser automatizado.',
                'type': 'AUTOMACAO',
                'subtype': 'novo',
                'priority': 'alta',
                'status': 'aberto',
                'dept_initials': 'FIN',
                'manual_process': '1. Baixar extrato do banco\n2. Importar no Excel\n3. Comparar manualmente com lançamentos\n4. Marcar conciliados um a um',
                'automation_name': 'Conciliação Bancária Automática',
            },
            {
                'subject': 'Atualizar tabela de impostos 2026',
                'description': 'As alíquotas de ICMS foram atualizadas para 2026 e precisam ser refletidas no sistema.',
                'type': 'ORQUESTRADOR',
                'subtype': 'atualizacao',
                'priority': 'urgente',
                'status': 'em_producao',
                'dept_initials': 'FIN',
            },
            # Tickets Comercial
            {
                'subject': 'CRM não sincroniza com e-mail',
                'description': 'Os e-mails enviados pelo CRM não estão sendo registrados no histórico do cliente.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'alta',
                'status': 'aberto',
                'dept_initials': 'COM',
            },
            {
                'subject': 'Dashboard de metas comerciais',
                'description': 'Criar um dashboard com visão geral das metas de vendas por vendedor e por equipe.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'normal',
                'status': 'recebido',
                'dept_initials': 'COM',
                'acceptance_criteria': '- Meta individual e por equipe\n- Gráfico de progresso\n- Ranking de vendedores\n- Período configurável',
            },
            {
                'subject': 'Automatizar envio de propostas',
                'description': 'O envio de propostas comerciais por e-mail é feito manualmente. Precisa de um fluxo automático após aprovação.',
                'type': 'AUTOMACAO',
                'subtype': 'novo',
                'priority': 'normal',
                'status': 'aberto',
                'dept_initials': 'COM',
                'manual_process': '1. Gerar proposta no sistema\n2. Exportar PDF\n3. Abrir e-mail\n4. Anexar e enviar manualmente',
                'automation_name': 'Envio Automático de Propostas',
            },
            # Tickets de Operações
            {
                'subject': 'Falha no monitoramento de servidores',
                'description': 'O sistema de monitoramento não está enviando alertas quando um servidor fica offline.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'urgente',
                'status': 'em_desenvolvimento',
                'dept_initials': 'OPS',
            },
            {
                'subject': 'Automatizar backup diário',
                'description': 'O backup dos bancos de dados de produção precisa ser automatizado com retenção de 30 dias.',
                'type': 'AUTOMACAO',
                'subtype': 'novo',
                'priority': 'alta',
                'status': 'em_producao',
                'dept_initials': 'OPS',
                'manual_process': '1. Conectar no servidor via SSH\n2. Executar script de dump\n3. Comprimir arquivo\n4. Copiar para storage\n5. Limpar backups antigos manualmente',
                'automation_name': 'Backup Automatizado DB',
            },
            {
                'subject': 'Implementar pipeline CI/CD',
                'description': 'Precisamos de um pipeline de integração e entrega contínua para o projeto principal.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'alta',
                'status': 'recebido',
                'dept_initials': 'OPS',
                'acceptance_criteria': '- Build automático em push\n- Testes unitários\n- Deploy em staging automático\n- Deploy em produção com aprovação',
            },
            # Tickets Jurídico
            {
                'subject': 'Sistema de gestão de contratos',
                'description': 'Precisamos de um módulo para gerenciar contratos com alertas de vencimento e renovação.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'alta',
                'status': 'aberto',
                'dept_initials': 'JUR',
                'acceptance_criteria': '- Cadastro de contratos\n- Upload de documentos\n- Alertas 30/60/90 dias antes do vencimento\n- Histórico de aditivos',
            },
            {
                'subject': 'Adequação LGPD - Termo de consentimento',
                'description': 'É necessário implementar o termo de consentimento de uso de dados pessoais conforme LGPD em todos os formulários.',
                'type': 'ORQUESTRADOR',
                'subtype': 'melhoria',
                'priority': 'urgente',
                'status': 'em_desenvolvimento',
                'dept_initials': 'JUR',
            },
            # Tickets com status cancelado/não atendido
            {
                'subject': 'Integrar com sistema legado (descontinuado)',
                'description': 'Integração com sistema antigo de folha de pagamento. Cancelado pois o sistema será desativado.',
                'type': 'ORQUESTRADOR',
                'subtype': 'nova_funcionalidade',
                'priority': 'normal',
                'status': 'cancelado',
                'dept_initials': 'TI',
                'justification': 'Sistema legado será desativado em 60 dias, integração não faz sentido.',
            },
            {
                'subject': 'Alterar cor do logo no sistema',
                'description': 'Solicitação para trocar a cor do logo na tela de login de azul para verde.',
                'type': 'ORQUESTRADOR',
                'subtype': 'melhoria',
                'priority': 'normal',
                'status': 'nao_atendido',
                'dept_initials': 'COM',
                'justification': 'Não é escopo de TI. Encaminhar para equipe de Design/Marketing.',
            },
            # Mais tickets variados
            {
                'subject': 'Melhoria na tela de pesquisa',
                'description': 'A pesquisa precisa de filtros avançados: por data, por departamento e por responsável.',
                'type': 'ORQUESTRADOR',
                'subtype': 'melhoria',
                'priority': 'normal',
                'status': 'aberto',
                'dept_initials': 'TI',
            },
            {
                'subject': 'Automatizar geração de notas fiscais',
                'description': 'As notas fiscais são geradas manualmente no portal da prefeitura. Automatizar o processo.',
                'type': 'AUTOMACAO',
                'subtype': 'novo',
                'priority': 'alta',
                'status': 'recebido',
                'dept_initials': 'FIN',
                'manual_process': '1. Acessar portal da prefeitura\n2. Preencher dados manualmente\n3. Gerar NF\n4. Download do PDF\n5. Enviar ao cliente',
                'automation_name': 'Geração de NF-e Automática',
            },
            {
                'subject': 'Erro de permissão no módulo de compras',
                'description': 'Usuários com perfil "Comprador" não conseguem aprovar pedidos acima de R$ 5.000. O botão de aprovação não aparece.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'alta',
                'status': 'aberto',
                'dept_initials': 'FIN',
                'steps': '1. Logar como Comprador\n2. Acessar Pedidos > Pendentes\n3. Abrir pedido acima de R$ 5.000\n4. Botão "Aprovar" não aparece',
                'unexpected_behavior': 'Botão de aprovação não é renderizado.',
                'normal_behavior': 'O botão deveria aparecer para pedidos dentro da alçada do comprador.',
            },
            {
                'subject': 'Relatório de horas extras inconsistente',
                'description': 'O relatório de horas extras mostra valores diferentes do esperado para o mês de março/2026.',
                'type': 'ORQUESTRADOR',
                'subtype': 'correcao_bug',
                'priority': 'normal',
                'status': 'aberto',
                'dept_initials': 'RH',
            },
        ]

        dept_map = {d.initials: d for d in departments}
        protocol_counter = Ticket.objects.aggregate(max=__import__('django').db.models.Max('protocol'))['max'] or 0
        tickets = []

        for i, t in enumerate(ticket_data):
            protocol_counter += 1
            dept = dept_map[t.pop('dept_initials')]

            # Escolhe um autor que tenha acesso ao departamento
            possible_authors = [
                u for u in authors
                if u.role == 'gestor_unidade' and
                UserDepartment.objects.filter(user=u, department=dept).exists()
            ] or [
                u for u in authors
                if UserDepartment.objects.filter(user=u, department=dept).exists()
            ] or authors

            author = random.choice(possible_authors)

            # Gera datas variadas nos últimos 60 dias
            days_ago = random.randint(1, 60)
            created = timezone.now() - timedelta(days=days_ago)

            ticket = Ticket.objects.create(
                protocol=protocol_counter,
                author=author,
                department=dept,
                type=t.pop('type'),
                subtype=t.pop('subtype'),
                subject=t.pop('subject'),
                description=t.pop('description'),
                priority=t.pop('priority'),
                status=t.pop('status'),
                url_system=t.pop('url_system', None),
                steps=t.pop('steps', None),
                normal_behavior=t.pop('normal_behavior', None),
                unexpected_behavior=t.pop('unexpected_behavior', None),
                justification=t.pop('justification', None),
                acceptance_criteria=t.pop('acceptance_criteria', None),
                manual_process=t.pop('manual_process', None),
                automation_name=t.pop('automation_name', None),
                notify_by_email=random.choice([True, False]),
            )
            # Atualiza created_at manualmente
            Ticket.objects.filter(pk=ticket.pk).update(created_at=created)

            tickets.append(ticket)
            self.stdout.write(f'  [criado] #{ticket.protocol} - {ticket.subject[:50]}')

        return tickets

    def _create_comments(self, tickets, users):
        atendentes = [u for u in users if u.role in ('admin', 'atendente')]
        clientes_gestores = [u for u in users if u.role in ('cliente', 'gestor_unidade')]

        comment_templates = [
            # Comentários de atendentes
            ('Recebemos sua solicitação e estamos analisando. Em breve daremos um retorno.', True),
            ('Conseguimos reproduzir o erro reportado. Estamos trabalhando na correção.', True),
            ('A correção foi aplicada no ambiente de testes. Poderia validar por favor?', False),
            ('Alinhamento interno: precisamos envolver a equipe de infraestrutura.', True),
            ('Deploy realizado no ambiente de staging. Favor testar e confirmar.', False),
            ('Priorizamos este ticket para o sprint atual.', True),
            ('Estamos aguardando liberação do ambiente de produção para deploy.', True),
            # Comentários de clientes/gestores
            ('Obrigado pelo retorno! Vou verificar e confirmo.', False),
            ('Testei e o problema persiste. Segue screenshot em anexo.', False),
            ('Funcionou perfeitamente! Podem encerrar o chamado.', False),
            ('Quando teremos uma previsão de entrega?', False),
            ('Esse problema está impactando a operação. Poderiam priorizar?', False),
            ('Validei no ambiente de testes e está OK. Podem subir para produção.', False),
        ]

        count = 0
        for ticket in tickets:
            # Tickets abertos geralmente têm menos comentários
            if ticket.status == 'aberto':
                num_comments = random.randint(0, 2)
            elif ticket.status in ('cancelado', 'nao_atendido'):
                num_comments = random.randint(1, 3)
            else:
                num_comments = random.randint(2, 5)

            for j in range(num_comments):
                # Alterna entre atendente e cliente
                if j % 2 == 0:
                    author = random.choice(atendentes)
                    pool = [c for c in comment_templates if c[1] or random.random() > 0.5]
                else:
                    author = random.choice(clientes_gestores)
                    pool = [c for c in comment_templates if not c[1] or random.random() > 0.7]

                text, internal = random.choice(pool)
                # Só atendentes fazem comentários internos
                if author.role in ('cliente', 'gestor_unidade'):
                    internal = False

                created = ticket.created_at + timedelta(hours=random.randint(1, 72 * (j + 1)))

                comment = Comment.objects.create(
                    ticket=ticket,
                    author=author,
                    comment=text,
                    internal=internal,
                )
                Comment.objects.filter(pk=comment.pk).update(created_at=created)
                count += 1

        self.stdout.write(f'  {count} comentários criados')

    def _create_status_logs(self, tickets, users):
        atendentes = [u for u in users if u.role in ('admin', 'atendente')]

        # Cria logs de transição coerentes com o status final
        transition_paths = {
            'aberto': [],
            'recebido': [('aberto', 'recebido')],
            'em_desenvolvimento': [('aberto', 'recebido'), ('recebido', 'em_desenvolvimento')],
            'em_producao': [('aberto', 'recebido'), ('recebido', 'em_desenvolvimento'), ('em_desenvolvimento', 'em_producao')],
            'aguardando_cliente': [('aberto', 'recebido'), ('recebido', 'em_desenvolvimento'), ('em_desenvolvimento', 'em_producao'), ('em_producao', 'aguardando_cliente')],
            'nao_atendido': [('aberto', 'recebido'), ('recebido', 'nao_atendido')],
            'cancelado': [('aberto', 'recebido'), ('recebido', 'cancelado')],
        }

        count = 0
        for ticket in tickets:
            path = transition_paths.get(ticket.status, [])
            for i, (old, new) in enumerate(path):
                changed_by = random.choice(atendentes)
                created = ticket.created_at + timedelta(hours=random.randint(1, 24) * (i + 1))

                justification = None
                if new == 'nao_atendido':
                    justification = ticket.justification or 'Solicitação fora do escopo.'
                elif new == 'cancelado':
                    justification = ticket.justification or 'Solicitação cancelada a pedido.'

                log = TicketStatusLog.objects.create(
                    ticket=ticket,
                    changed_by=changed_by,
                    old_status=old,
                    new_status=new,
                    justification=justification,
                )
                TicketStatusLog.objects.filter(pk=log.pk).update(created_at=created)
                count += 1

        self.stdout.write(f'  {count} logs de status criados')
