# TOC — Template Orquestrador de Chamados

Sistema de gestão de chamados desenvolvido para o **Núcleo de Automação de Procedimentos do TJGO**, integrado ao Orquestrador DPE.

---

## Stack Tecnológica

- **Backend**: Django 6.x + Python 3.12
- **Frontend**: Django Templates + HTMX 2.x + Alpine.js 3.x + Bootstrap 5.3
- **Banco de Dados**: PostgreSQL 17
- **Storage**: MinIO (Desenvolvimento) / AWS S3 (Produção)
- **Autenticação**: django-allauth (utilizando email como identificador principal)

---

## Pré-requisitos

- Python 3.12+
- PostgreSQL 17 (via contêiner Docker ou instalação local)
- MinIO (via contêiner Docker)
- Git e Docker instalados

---

## Setup de Desenvolvimento

### 1. Clonar o repositório

```bash
git clone git@github.com:murilonegrao/toc.git
cd toc
```

### 2. Configurar o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Linux/Mac
# venv\Scripts\activate   # No Windows
```

### 3. Instalar as dependências

```bash
pip install -r requirements/development.txt
```

### 4. Configurar as variáveis de ambiente

Copie o arquivo de exemplo e preencha com seus ambientes locais:

```bash
cp .env.example .env
```

*Exemplo de variáveis obrigatórias no `.env`:*

```env
SECRET_KEY=sua-secret-key-muito-segura
DATABASE_URL=postgresql://toc_user:sua_senha@localhost:5432/toc_database
DJANGO_SETTINGS_MODULE=config.settings.development
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=toc-attachments
S3_ENDPOINT_URL=http://localhost:9000
S3_REGION_NAME=us-east-1
```

### 5. Iniciar o banco de dados (PostgreSQL)

```bash
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=toc_user \
  -e POSTGRES_PASSWORD=sua_senha \
  -e POSTGRES_DB=toc_database \
  postgres:17-alpine
```

Em seguida, acesse o contêiner e conceda as permissões necessárias (obrigatório para o PostgreSQL 15+):

```bash
docker exec -it postgres psql -U postgres -d toc_database
```

```sql
GRANT ALL ON SCHEMA public TO toc_user;
```

### 6. Iniciar o Storage Local (MinIO)

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

Acesse o console do MinIO pelo navegador em `http://localhost:9001` e crie manualmente o bucket chamado `toc-attachments`.

### 7. Executar as migrações do banco

```bash
python manage.py migrate
```

### 8. Criar o superusuário

Acesse o shell interativo do Django:

```bash
python manage.py shell
```

E execute o comando para criar um perfil de administrador inicial:

```python
from apps.accounts.models import User

User.objects.create_superuser(
    email='admin@toc.com',
    password='sua_senha',
    name='Admin TOC',
    role='admin',
    is_approved=True,
)
```

### 9. Criar registros iniciais (Departamentos)

Aproveitando o shell previamente aberto, cadastre alguns departamentos essenciais para testar o sistema:

```python
from apps.departments.models import Department

Department.objects.create(name='CAC', initials='CAC', color='#F4645F', active=True)
Department.objects.create(name='CCARPV', initials='CCARPV', color='#4A90D9', active=True)

exit()  # Pressione ENTER para sair do shell interativo
```

### 10. Iniciar o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse o sistema no navegador acessando `http://localhost:8000`.

---

## Estrutura do Projeto

```text
toc/
├── apps/
│   ├── accounts/        # Controle de usuários, autenticação e aprovações
│   ├── attachments/     # Gerenciador de upload de arquivos para S3/MinIO
│   ├── comments/        # Lógica de comentários e interações nos chamados
│   ├── core/            # Dashboard principal e views genéricas base
│   ├── departments/     # Gestão dos Departamentos / Centrais do TJGO
│   ├── notifications/   # Log de atividades e disparos
│   └── tickets/         # Módulo principal: Chamados (CRUD, status, histórico)
├── config/
│   └── settings/
│       ├── base.py        # Configurações globais e comuns
│       ├── development.py # Configuração exclusiva de ambiente dev (debug ativado)
│       └── production.py  # Configurações otimizadas para deploy em produção
├── static/
│   └── css/main.css     # Estilos globais complementares (Vanilla CSS)
├── templates/
│   ├── account/         # Sobrescrita das views nativas do django-allauth
│   ├── accounts/        # Templates customizados para o fluxo de contas (pending, etc)
│   ├── tickets/         # Interfaces e formulários de chamados / kanban
│   └── base_app.html    # Layout base contendo sidebar, topbar e tags base
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## Papéis de Usuário (Roles)

| Papel | Acesso / Permissões no Sistema |
|---|---|
| `admin` | Acesso total e irrestrito ao sistema gerencial e Painel do Django Admin |
| `atendente` | Permissão para visualizar/gerir todos os chamados e aprovar novos cadastros de usuários |
| `gestor_unidade` | Visão ampla sobre os chamados gerados dentros de seus respectivos departamentos |
| `cliente` | Visão restrita de apenas consultar e interagir com os seus próprios chamados |

---

## Fluxo de Status dos Chamados

Abaixo está o ciclo de vida padrão que ocorre num andamento de um chamado:

```text
Aberto → Recebido → Em Desenvolvimento → Em Produção → Aguardando Cliente → Finalizado
                  ↘ Não Atendido                     ↘ Não Atendido
```

Para uma melhor visualização do fluxo de estados:

```mermaid
graph LR
    A[Aberto] --> B[Recebido]
    A --> N1[Não Atendido]
    B --> C[Em Desenvolvimento]
    C --> D[Em Produção]
    C --> N2[Não Atendido]
    D --> E[Aguardando Cliente]
    E --> F[Finalizado]
```

---

## Fluxo de Cadastro de Usuários

1. Usuário prospecto acessa as telas de Login e se cadastra na rota `/accounts/signup/`.
2. Após salvar o usuário simples, ele deve escolher qual o departamento de alocação em `/accounts/select-department/`.
3. Após isso, a conta do servidor do TJ ficará trancada em status **pendente**, redirecionando sempre sua página inicial para `/accounts/pending/`.
4. Um atendente autorizado ou um administrador vai visualizar uma chamada em sua Dashboard em `Aprovações Pendentes` e clicar em `/accounts/pending-users/` para habilitar ou rejeitar a liberação de rede daquele cadastro.
5. Após este _Ok_ de segurança, o usuário passará a integrar oficialmente a listagem acessando as funcionalidades em seu Papel ("Role") respectiva.

---

## Convenções de Commits do Git

Este projeto impõe/sugere a prática de [Conventional Commits](https://www.conventionalcommits.org/):

| Padrão | Cenário a ser adotado |
|---|---|
| `feat:` | Utilizado no lançamento uma nova Feature ou Funcionalidade ao sistema |
| `fix:` | Usado para a correção de algum comportamento anômalo/bug |
| `chore:` | Utilizado quando foram feitos setups de ambiente, mudanças de lib/dependências ou script de configuração CI/CD |
| `docs:` | Quando existem mudanças em documentações e comentários de forma expressiva e substancial (ex: atualizar o README) |
| `refactor:` | Se ocorreu uma refatoração em base de lógica ou banco, sem alterar visivelmente o escopo comportamental final do software |