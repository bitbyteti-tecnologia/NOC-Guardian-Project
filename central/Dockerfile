# ==============================================================================
# Dockerfile - Guardian Central API
# ==============================================================================
# Imagem base leve baseada em Debian (Slim) compatível com ARM64 e x86-64
FROM python:3.9-slim

# Define diretório de trabalho
WORKDIR /app

# Instalação de dependências
# Copiamos apenas o requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte da aplicação
COPY . .

# Expõe a porta padrão da API
EXPOSE 8000

# Comando de inicialização
# uvicorn inicia o servidor ASGI de alta performance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
