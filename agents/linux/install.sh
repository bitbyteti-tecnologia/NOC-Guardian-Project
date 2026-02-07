#!/bin/bash
# Script de Instalação do Guardian Agent (Linux)
# Executar como root

if [ "$EUID" -ne 0 ]; then 
  echo "Por favor, execute como root (sudo)"
  exit 1
fi

INSTALL_DIR="/opt/guardian-agent"
CONFIG_DIR="/etc/guardian-agent"
SERVICE_FILE="/etc/systemd/system/guardian-agent.service"

echo "=== Instalando Guardian Agent Enterprise ==="

# 1. Instalar dependências (Python3 e Pip)
echo "[1/5] Verificando dependências..."
if command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y python3 python3-pip
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip
fi

# Instalar libs Python
pip3 install -r ../requirements.txt

# 2. Criar Usuário de Serviço
echo "[2/5] Criando usuário de serviço..."
id -u guardian-agent &>/dev/null || useradd -r -s /bin/false guardian-agent

# 3. Copiar Arquivos
echo "[3/5] Copiando arquivos..."
mkdir -p $INSTALL_DIR
mkdir -p $CONFIG_DIR

cp ../guardian_agent.py $INSTALL_DIR/
cp ../config.yaml.example $CONFIG_DIR/config.yaml

# Ajustar permissões
chown -R guardian-agent:guardian-agent $INSTALL_DIR
chown -R guardian-agent:guardian-agent $CONFIG_DIR
chmod 600 $CONFIG_DIR/config.yaml

# 4. Instalar Serviço Systemd
echo "[4/5] Configurando Systemd..."
cp guardian-agent.service $SERVICE_FILE
systemctl daemon-reload

# 5. Finalização
echo "[5/5] Instalação concluída!"
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Edite o arquivo de configuração com sua API KEY:"
echo "   nano $CONFIG_DIR/config.yaml"
echo ""
echo "2. Inicie o serviço:"
echo "   systemctl enable guardian-agent"
echo "   systemctl start guardian-agent"
echo ""
echo "3. Verifique o status:"
echo "   systemctl status guardian-agent"
