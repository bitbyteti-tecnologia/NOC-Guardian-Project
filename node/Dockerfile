# ==============================================================================
# Dockerfile - Guardian NODE
# ==============================================================================
# Imagem base leve baseada em Debian (Slim) compatível com ARM64 e x86-64
FROM python:3.9-slim

# Define variáveis para evitar arquivos .pyc e logs presos em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalação de dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cria usuário não-root para segurança (Hardening)
RUN useradd -m guardian_user

# Copia o código fonte
COPY . .

# Ajusta permissões
RUN chown -R guardian_user:guardian_user /app

# Troca para usuário seguro
USER guardian_user

# Inicia o coletor
CMD ["python", "collector.py"]
