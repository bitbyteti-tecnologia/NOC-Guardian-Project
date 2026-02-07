#!/bin/bash

# ==========================================
# NOC GUARDIAN - SERVER SETUP SCRIPT
# ==========================================
# Este script prepara o servidor Ubuntu para receber o deploy.
# Ele instala Docker, cria as pastas e ajusta permissões.
#
# COMO USAR:
# 1. Copie este arquivo para o servidor
# 2. Dê permissão: chmod +x setup_server.sh
# 3. Execute: sudo ./setup_server.sh
# ==========================================

set -e

echo ">>> [1/5] Atualizando sistema e instalando dependências..."
sudo apt-get update -qq
sudo apt-get install -y git docker.io docker-compose-plugin curl

echo ">>> [2/5] Configurando Docker..."
sudo systemctl enable docker
sudo systemctl start docker
# Adiciona o usuário atual ao grupo docker para não precisar de sudo
sudo usermod -aG docker $USER || true

echo ">>> [3/5] Criando diretório do projeto..."
TARGET_DIR="/opt/NOC-Guardian-Project"

if [ ! -d "$TARGET_DIR" ]; then
    sudo mkdir -p "$TARGET_DIR"
    echo "Diretório criado: $TARGET_DIR"
else
    echo "Diretório já existe: $TARGET_DIR"
fi

# Ajusta permissões para o usuário atual
sudo chown -R $USER:$USER "$TARGET_DIR"
sudo chmod -R 775 "$TARGET_DIR"

echo ">>> [4/5] Verificando configuração SSH..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Adiciona a chave fornecida pelo usuário (garantia de acesso)
KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqLTHEXQnjbmBXlTq7QvdFydDliSD17sA3iS7Np0KBBJoLsOS2mwyUFhEsbxeKv07oPXA1ClakWXPAFAkszPnb1+07PZp7QpINxQmdOM43uFdOV3JH+8Ca8s6FyzNkfm2HzRSZLSpUMeginBNePFYvYhCT9O8A2VDIwZ90L7VpY3QjSrrp1IZ7x4eYGzUs3vX7ZN/HALU5Li3++ESSrdy7kGJWFe8+/ACD+WrhRmbIA/7hy5ZvLNCYUcS9bxCAkDhZwDh2eCuvVxyCXUTdKS9dgH/kQGL1JNQaMFHnhGMaLUAdR72xACdl82VZc9VfcxhOKHrj2ar+Hpge1hOuHWsh rsa-key-20220219"

if ! grep -q "$KEY" ~/.ssh/authorized_keys; then
    echo "$KEY" >> ~/.ssh/authorized_keys
    echo "Chave SSH adicionada com sucesso."
else
    echo "Chave SSH já estava configurada."
fi

echo ">>> [5/5] CONCLUÍDO!"
echo "===================================================="
echo "SEU SERVIDOR ESTÁ PRONTO."
echo "===================================================="
echo "Para finalizar a conexão com o GitHub:"
echo "1. Pegue sua CHAVE PÚBLICA (id_rsa.pub) da sua máquina local."
echo "2. Cole ela dentro do arquivo ~/.ssh/authorized_keys neste servidor."
echo "3. O IP deste servidor é:"
curl -s ifconfig.me
echo ""
echo "===================================================="
