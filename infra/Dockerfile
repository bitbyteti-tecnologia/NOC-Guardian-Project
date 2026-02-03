# ==============================================================================
# Dockerfile Multi-Arch (Guardian NODE)
# ==============================================================================
# Este Dockerfile é configurado para suportar múltiplas arquiteturas (x86-64 e ARM64),
# permitindo o deploy tanto em servidores potentes quanto em Raspberry Pis.
#
# Base Image: Python 3.9 Slim (Debian-based) para menor tamanho e superfície de ataque.
# ==============================================================================

# Etapa 1: Build da Imagem Base
FROM python:3.9-slim as base

# Define variáveis de ambiente para evitar arquivos .pyc e buffer de stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# ==============================================================================
# Etapa 2: Instalação de Dependências
# ==============================================================================
# Copia o arquivo de requisitos primeiro para aproveitar o cache de camadas do Docker
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Etapa 3: Hardening e Segurança (Camada de Infraestrutura)
# ==============================================================================
# Cria um usuário não-root para executar a aplicação.
# Rodar como root dentro do container é uma falha de segurança grave.
RUN useradd -m guardian_user

# Copia o código fonte do NODE para o container
COPY ../node /app/node

# Ajusta as permissões para o usuário não-root
RUN chown -R guardian_user:guardian_user /app

# Troca para o usuário seguro
USER guardian_user

# ==============================================================================
# Etapa 4: Execução
# ==============================================================================
# Comando padrão para iniciar o coletor
CMD ["python", "node/collector.py"]
