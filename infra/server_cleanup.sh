#!/bin/bash
# ==============================================================================
# Script de Limpeza Radical do Docker
# ==============================================================================
# ATENÇÃO: Este script irá parar e remover TODOS os containers, redes e imagens
# não utilizados no servidor. Use com cautela se tiver outros projetos rodando!
# ==============================================================================

echo "🛑 Parando todos os containers em execução..."
docker stop $(docker ps -aq) 2>/dev/null

echo "🗑️ Removendo todos os containers..."
docker rm $(docker ps -aq) 2>/dev/null

echo "🧹 Limpando redes, imagens e volumes não utilizados (Prune)..."
docker system prune -af --volumes

echo "✅ Limpeza concluída! O servidor está pronto para o novo deploy."
