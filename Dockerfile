# Usa a imagem oficial do Python 3.12 na versão slim (mais leve)
FROM python:3.12-slim

# Evita que o Python gere arquivos de bytecode (.pyc)
ENV PYTHONDONTWRITEBYTECODE=1
# Força o Python a printar no console imediatamente (útil para ver logs do docker)
ENV PYTHONUNBUFFERED=1

# Instalar as dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do Python
# Copiamos os requirements primeiro para aproveitar o layer cache do Docker
COPY requirements/ ./requirements/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements/production.txt

# Copia todo o código restante pro container
COPY . .

# Cria os arquivos de mídia e estáticos no processo de build.
# Fornecemos variáveis falsas para o env apenas para o Django não quebrar de falta de credenciais durante a montagem do container.
RUN DJANGO_SETTINGS_MODULE="config.settings.production" \
    SECRET_KEY="fake-key-for-build" \
    DATABASE_URL="sqlite:///:memory:" \
    S3_ACCESS_KEY_ID="dummy" \
    S3_SECRET_ACCESS_KEY="dummy" \
    S3_BUCKET_NAME="dummy" \
    S3_ENDPOINT_URL="http://dummy" \
    python manage.py collectstatic --noinput --clear

# Expor a porta 8000 para trafegar
EXPOSE 8000

# Executa o Gunicorn como visto na recomendação (usando 3 workers)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--access-logfile", "-"]
