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

# Permissões (seguro para rodar como root ou user)
sudo chown -R $USER:$USER "$TARGET_DIR"
sudo chmod -R 775 "$TARGET_DIR"

echo ">>> [4/5] Verificando configuração SSH..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Adiciona a chave fornecida pelo usuário (garantia de acesso)
KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqLTHEXQnjbmBXlTq7QvdFydDliSD17sA3iS7Np0KBBJoLsOS2mwyUFhEsbxeKv07oPXA1ClakWXPAFAkszPnb1+07PZp7QpINxQmdOM43uFdOV3JH+8Ca8s6FyzNkfm2HzRSZLSpUMeginBNePFYvYhCT9O8A2VDIwZ90L7VpY3QjSrrp1IZ7x4eYGzUs3vX7ZN/HALU5Li3++ESSrdy7kGJWFe8+/ACD+WrhRmbIA/7hy5ZvLNCYUcS9bxCAkDhZwDh2eCuvVxyCXUTdKS9dgH/kQGL1JNQaMFHnhGMaLUAdR72xACdl82VZc9VfcxhOKHrj2ar+Hpge1hOuHWsh noc-guardian-deploy-key"

if ! grep -q "noc-guardian-deploy-key" ~/.ssh/authorized_keys; then
    echo "$KEY" >> ~/.ssh/authorized_keys
    echo "Chave SSH adicionada com sucesso."
else
    echo "Chave SSH já estava configurada."
fi

echo ">>> [5/5] CONCLUÍDO!"
echo "===================================================="
echo "SERVIDOR PREPARADO COM SUCESSO."
echo "Pode disparar o deploy no GitHub Actions agora."
echo "===================================================="
