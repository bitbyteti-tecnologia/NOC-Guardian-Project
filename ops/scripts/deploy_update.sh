#!/bin/bash
# ==============================================================================
# NOC GUARDIAN - SCRIPT DE ATUALIZAÇÃO (PRODUÇÃO LINUX)
# ==============================================================================
# Este script automatiza o processo de atualização do serviço Central e Proxy
# após alterações de código ou configuração.
#
# Uso: chmod +x deploy_update.sh && ./deploy_update.sh
# ==============================================================================

set -e # Aborta se ocorrer erro em qualquer comando

echo "=== [NOC GUARDIAN] INICIANDO PROCESSO DE ATUALIZAÇÃO ==="
echo "Data: $(date)"

# 1. Verificação de Pré-requisitos
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ ERRO: docker-compose.yml não encontrado no diretório atual."
    exit 1
fi

# 2. Atualização de Código (Git Pull)
# Descomente as linhas abaixo se você usa Git no servidor
# echo ">>> 📥 Atualizando repositório..."
# git pull origin main

# 3. Rebuild do Serviço Central
# Necessário porque o código Python está dentro da imagem, não em volume.
echo ">>> 🔨 Reconstruindo imagem do Guardian Central..."
docker compose up -d --build central

# 4. Atualização do Traefik (Proxy)
# Necessário apenas se houve mudança nas labels ou variáveis de ambiente do Traefik
echo ">>> 🔄 Atualizando configurações do Proxy..."
docker compose up -d traefik

# 5. Verificação de Saúde
echo ">>> 🏥 Aguardando inicialização para Health Check..."
sleep 5
if docker compose ps | grep -q "healthy"; then
    echo "✅ Serviços parecem saudáveis."
else
    echo "⚠️ AVISO: Alguns serviços podem não estar saudáveis. Verifique com 'docker compose ps'."
fi

# 6. Limpeza
echo ">>> 🧹 Removendo imagens antigas (dangling)..."
docker image prune -f

echo "=== [SUCESSO] ATUALIZAÇÃO CONCLUÍDA ==="
echo "📝 Para ver logs: docker compose logs -f central"
