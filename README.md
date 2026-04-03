# TOC — Template Orquestrador de Chamados

Sistema de gestão de chamados desenvolvido para o Núcleo de Automação de Procedimentos do TJGO, integrado ao Orquestrador DPE.

---

## Stack

- **Backend**: Django 6.x + Python 3.12
- **Frontend**: Django Templates + HTMX 2.x + Alpine.js 3.x + Bootstrap 5.3
- **Banco**: PostgreSQL 17
- **Storage**: MinIO (dev) / AWS S3 (produção)
- **Auth**: django-allauth com email como identificador

---

## Pré-requisitos

- Python 3.12+
- PostgreSQL 17 (container ou local)
- MinIO (container)
- Git

---

## Setup de desenvolvimento

### 1. Clone o repositório

```bash
git clone git@github.com:murilonegrao/toc.git
cd toc
```

### 2. Ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements/development.txt
```

### 4. Configure o `.env`

Copie o exemplo e preencha com seus valores:

```bash
cp .env.example .env
```

Variáveis obrigatórias:

```
SECRET_KEY=sua-secret-key
DATABASE_URL=postgresql://usuario:senha@localhost:5432/toc_database
DJANGO_SETTINGS_MODULE=config.settings.development
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=toc-attachments
S3_ENDPOINT_URL=http://localhost:9000
S3_REGION_NAME=us-east-1
```

### 5. Suba o PostgreSQL

```bash
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=toc_user \
  -e POSTGRES_PASSWORD=sua_senha \
  -e POSTGRES_DB=toc_database \
  postgres:17-alpine
```

Depois conecte e dê o grant necessário (PostgreSQL 15+):

```bash
docker exec -it postgres psql -U postgres -d toc_database
```

```sql
GRANT ALL ON SCHEMA public TO toc_user;
```

### 6. Suba o MinIO

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

Acesse `http://localhost:9001` e crie o bucket `toc-attachments`.

### 7. Rode as migrations

```bash
python manage.py migrate
```

### 8. Crie o superuser

```bash
python manage.py shell
```

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

### 9. Crie departamentos iniciais

```python
from apps.departments.models import Department
Department.objects.create(name='CAC', initials='CAC', color='#F4645F', active=True)
Department.objects.create(name='CCARPV', initials='CCARPV', color='#4A90D9', active=True)
```

### 10. Suba o servidor

```bash
python manage.py runserver
```

Acesse `http://localhost:8000`.

---

## Estrutura do projeto

```
toc/
├── apps/
│   ├── accounts/        # Usuários, autenticação, aprovação
│   ├── attachments/     # Upload de arquivos (MinIO/S3)
│   ├── comments/        # Comentários nos tickets
│   ├── core/            # Dashboard e views genéricas
│   ├── departments/     # Departamentos/Centrais
│   ├── notifications/   # Log de notificações
│   └── tickets/         # Chamados, status, histórico
├── config/
│   └── settings/
│       ├── base.py      # Configurações comuns
│       ├── development.py
│       └── production.py
├── static/
│   └── css/main.css     # CSS principal
├── templates/
│   ├── account/         # Templates do allauth (login, signup)
│   ├── accounts/        # Templates do app accounts
│   ├── tickets/         # Templates dos chamados
│   └── base_app.html    # Template base com sidebar
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## Papéis de usuário

| Papel | Acesso |
|---|---|
| `admin` | Acesso total ao sistema |
| `atendente` | Vê todos os chamados, aprova usuários |
| `gestor_unidade` | Vê chamados do próprio departamento |
| `cliente` | Vê só os próprios chamados |

---

## Fluxo de status dos chamados

```
aberto → recebido → em_desenvolvimento → em_producao → aguardando_cliente → finalizado
                ↘ nao_atendido          ↘ nao_atendido
```

---

## Fluxo de cadastro

1. Usuário se cadastra em `/accounts/signup/`
2. Seleciona o departamento em `/accounts/select-department/`
3. Aguarda aprovação — tela `/accounts/pending/`
4. Atendente ou admin aprova em `/accounts/pending-users/`
5. Usuário ganha acesso ao sistema com o papel atribuído

---

## Convenções de commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nova funcionalidade
fix: correção de bug
chore: setup, configuração
docs: documentação
refactor: refatoração sem mudança de comportamento
```