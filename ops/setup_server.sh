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

# Adiciona usuários ao grupo Docker
echo "Adicionando usuários ao grupo Docker..."
sudo usermod -aG docker $USER || true
sudo usermod -aG docker ubuntu || true

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
    
    # Corrige dono do diretório SSH
    chown -R ubuntu:ubuntu "$UBUNTU_SSH"
fi

# ============================================================================
# NOC GUARDIAN - HARDENING (MANDATÓRIO)
# ============================================================================
echo ">>> [5/5] Aplicando Hardening de Segurança (README Compliant)..."

# 1. Atualizações Automáticas
echo "Configurando Unattended Upgrades..."
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades || true

# 2. Firewall (UFW)
echo "Configurando UFW (Firewall)..."
if command -v ufw &> /dev/null; then
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    # Habilita sem pedir confirmação
    echo "y" | sudo ufw enable
    echo "✅ UFW Ativado: Portas 22, 80, 443 permitidas."
else
    echo "⚠️ UFW não instalado. Instalando..."
    sudo apt-get install -y ufw
    sudo ufw default deny incoming
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    echo "y" | sudo ufw enable
fi

# 3. Fail2Ban
echo "Configurando Fail2Ban..."
sudo apt-get install -y fail2ban
# Cria configuração local para não sobrescrever updates
if [ ! -f /etc/fail2ban/jail.local ]; then
    echo "[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600" | sudo tee /etc/fail2ban/jail.local
    sudo systemctl restart fail2ban
    echo "✅ Fail2Ban configurado para SSH."
fi

# 4. SSH Hardening (Desabilitar Root e Senhas)
echo "Aplicando SSH Hardening (Desabilitando Root Login e Password Auth)..."
SSHD_CONFIG="/etc/ssh/sshd_config"

# Backup do config original
if [ ! -f "${SSHD_CONFIG}.bak" ]; then
    sudo cp $SSHD_CONFIG "${SSHD_CONFIG}.bak"
fi

# Ajustes de segurança
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' $SSHD_CONFIG
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' $SSHD_CONFIG
sudo sed -i 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' $SSHD_CONFIG
sudo sed -i 's/^#*UsePAM.*/UsePAM yes/' $SSHD_CONFIG

# Reinicia SSH para aplicar (se syntax ok)
if sudo sshd -t; then
    if systemctl list-units --full -all | grep -Fq "ssh.service"; then
        sudo systemctl restart ssh || echo "⚠️ Falha ao reiniciar serviço 'ssh'"
    elif systemctl list-units --full -all | grep -Fq "sshd.service"; then
        sudo systemctl restart sshd || echo "⚠️ Falha ao reiniciar serviço 'sshd'"
    else
        echo "⚠️ Serviço SSH não identificado automaticamente. Reinicie manualmente."
    fi
    echo "✅ SSH Hardening aplicado com sucesso."
else
    echo "❌ Erro na configuração do SSH. Revertendo..."
    sudo cp "${SSHD_CONFIG}.bak" $SSHD_CONFIG
    sudo systemctl restart sshd
fi

# 5. Kernel Hardening (Network Stack)
echo "Aplicando Kernel Hardening..."
cat <<EOF | sudo tee /etc/sysctl.d/99-guardian-security.conf
# Proteção contra IP Spoofing
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Desabilitar redirecionamentos ICMP (Man-in-the-Middle)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# Ignorar pings de broadcast (Smurf attack protection)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Habilitar proteção contra SYN Flood
net.ipv4.tcp_syncookies = 1

# Desabilitar Source Routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
EOF

# Aplica configurações
sudo sysctl -p /etc/sysctl.d/99-guardian-security.conf
echo "✅ Kernel Hardening aplicado."

echo "=========================================="
echo "✅ SETUP E HARDENING CONCLUÍDOS!"
echo "=========================================="
echo "Pode disparar o deploy no GitHub Actions agora."
echo "===================================================="
