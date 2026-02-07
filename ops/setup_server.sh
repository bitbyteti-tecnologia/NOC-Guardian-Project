#!/bin/bash

# ==========================================
# NOC GUARDIAN - SERVER SETUP SCRIPT (V2)
# ==========================================

set -e

echo ">>> [1/5] Verificando ambiente Docker..."

# Verifica se Docker já existe para evitar conflitos de pacotes (Erro containerd.io)
if command -v docker &> /dev/null; then
    echo "✅ Docker já detectado. Pulando instalação para evitar conflitos."
else
    echo "⚠️ Docker não encontrado. Iniciando instalação robusta..."
    
    # Remove pacotes conflitantes antigos, se houver
    echo "Limpando versões antigas/conflitantes..."
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
        sudo apt-get remove -y $pkg || true
    done

    # Instala via script oficial (trata melhor as dependências do Ubuntu)
    echo "Instalando Docker via script oficial..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
fi

# Garante apenas as ferramentas essenciais
echo "Verificando git e curl..."
sudo apt-get update -qq
sudo apt-get install -y git curl

echo ">>> [2/5] Configurando Serviço Docker..."
sudo systemctl enable docker
sudo systemctl start docker

echo ">>> [3/5] Criando diretório do projeto..."
TARGET_DIR="/opt/NOC-Guardian-Project"

if [ ! -d "$TARGET_DIR" ]; then
    sudo mkdir -p "$TARGET_DIR"
    echo "Diretório criado: $TARGET_DIR"
else
    echo "Diretório já existe: $TARGET_DIR"
fi

# Define usuário proprietário (ubuntu se existir, senão o atual)
OWNER="ubuntu"
if ! id "$OWNER" &>/dev/null; then
    OWNER="$USER"
fi

# Permissões recursivas
echo "Ajustando permissões para usuário: $OWNER"
sudo chown -R $OWNER:$OWNER "$TARGET_DIR"
sudo chmod -R 775 "$TARGET_DIR"

echo ">>> [4/5] Verificando configuração SSH..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Chaves SSH (Usuário + Deploy)
USER_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqLTHEXQnjbmBXlTq7QvdFydDliSD17sA3iS7Np0KBBJoLsOS2mwyUFhEsbxeKv07oPXA1ClakWXPAFAkszPnb1+07PZp7QpINxQmdOM43uFdOV3JH+8Ca8s6FyzNkfm2HzRSZLSpUMeginBNePFYvYhCT9O8A2VDIwZ90L7VpY3QjSrrp1IZ7x4eYGzUs3vX7ZN/HALU5Li3++ESSrdy7kGJWFe8+/ACD+WrhRmbIA/7hy5ZvLNCYUcS9bxCAkDhZwDh2eCuvVxyCXUTdKS9dgH/kQGL1JNQaMFHnhGMaLUAdR72xACdl82VZc9VfcxhOKHrj2ar+Hpge1hOuHWsh rsa-key-20220219"
DEPLOY_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC83d5euvI1u44Et5M0RunM4tEDS9I83e2h/JqjXjXw0VsRWen2CL9aSa07NOeJ3pQeQke5tb8d0Ncy0Im5Sust5q2k1OGdcqcewyelnrx0FGWOUrAlPVsN8zBshFwpKimeXubT6F7Rgytokmbn/Bm6ckIvXqNKTdipn+aDw3K0QQlHLDFfiu2gsivz/Ukva7DxFh+IqF4os38P31DjCV9PnPia/jurAF5m6Rovn83SIAKeS5WMFpAui5tvBDfa3gug+YW7ricmBa+GErC48mUxQE9iZzpv63ASlumgwnN+J7fiZjIy+GOUnU6ghruEEe6FJ2XB/KDzIVK1Hi+fbyefr9Ucj95vQA+4Ljlehh5R/TT/ihpHOfXMrhD4gjF9eOe7siuP9U0SItCdCzPgrAHTAmNfkSlDMlyNUcsGYCfKX8tToNAn8WC+nU67SDpxU/fYvFqqvajLZnYzf3+WgnkgVk3eSi58Fmuq64WL1A80x+MO57iVTp10a84BVfXRntRIQ1BkUF54u/f9L6ljKxpTR3Z+fbeKrVBug08PS+T8qu9VCSNXSRMAhTHtSuoBNeCseROtSrbqJUD4JfRc7WpYT/ZVYEqu6B9bYIzL/5hahR5DMO1PdLZeb9txMShz0W/MTJ+Z34b6VlLUYqMjAAHsTfdVs8H1ERLaC9P9VwpO8w== noc-guardian-deploy-key"

# 1. Adiciona chave do usuário (Se não existir)
if ! grep -q "rsa-key-20220219" ~/.ssh/authorized_keys; then
    echo "$USER_KEY" >> ~/.ssh/authorized_keys
    echo "✅ Chave pessoal adicionada."
else
    echo "ℹ️ Chave pessoal já configurada."
fi

# 2. Adiciona chave de deploy (Se não existir)
if ! grep -q "noc-guardian-deploy-key" ~/.ssh/authorized_keys; then
    echo "$DEPLOY_KEY" >> ~/.ssh/authorized_keys
    echo "✅ Chave de deploy adicionada."
else
    echo "ℹ️ Chave de deploy já configurada."
fi

# ============================================================================
# CORREÇÃO PARA USUÁRIO UBUNTU (Caso o script rode como root mas o deploy use ubuntu)
# ============================================================================
if id "ubuntu" &>/dev/null; then
    echo ">>> Detectado usuário 'ubuntu'. Configurando chaves para ele também..."
    
    UBUNTU_SSH="/home/ubuntu/.ssh"
    mkdir -p "$UBUNTU_SSH"
    chmod 700 "$UBUNTU_SSH"
    touch "$UBUNTU_SSH/authorized_keys"
    chmod 600 "$UBUNTU_SSH/authorized_keys"

    # Adiciona chaves para o usuário ubuntu
    if ! grep -q "rsa-key-20220219" "$UBUNTU_SSH/authorized_keys"; then
        echo "$USER_KEY" >> "$UBUNTU_SSH/authorized_keys"
        echo "✅ Chave pessoal adicionada para 'ubuntu'."
    fi

    if ! grep -q "noc-guardian-deploy-key" "$UBUNTU_SSH/authorized_keys"; then
        echo "$DEPLOY_KEY" >> "$UBUNTU_SSH/authorized_keys"
        echo "✅ Chave de deploy adicionada para 'ubuntu'."
    fi
    
    # Corrige permissões
    chown -R ubuntu:ubuntu "$UBUNTU_SSH"
fi

echo ">>> [5/5] CONCLUÍDO!"
echo "===================================================="
echo "SERVIDOR PREPARADO COM SUCESSO."
echo "Pode disparar o deploy no GitHub Actions agora."
echo "===================================================="
