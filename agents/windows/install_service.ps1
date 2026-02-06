# Script de Instalação do Serviço Guardian Agent (Windows)
# Requer NSSM (Non-Sucking Service Manager) ou pode usar sc.exe se for compatível
# Este script assume o uso de NSSM para maior robustez

$SERVICE_NAME = "GuardianAgent"
$INSTALL_DIR = "C:\GuardianAgent"
$SOURCE_DIR = $PSScriptRoot

# Verificar se executado como Admin
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

# 1. Criar diretório de instalação
if (!(Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force
    Write-Host "Diretório criado: $INSTALL_DIR"
}

# 2. Copiar arquivos
Copy-Item "$SOURCE_DIR\guardian-agent.exe" -Destination "$INSTALL_DIR\guardian-agent.exe" -Force
if (!(Test-Path "$INSTALL_DIR\config.yaml")) {
    Copy-Item "$SOURCE_DIR\config.yaml" -Destination "$INSTALL_DIR\config.yaml"
    Write-Host "Configuração padrão copiada. POR FAVOR, EDITE O ARQUIVO config.yaml COM SUA API KEY!"
}

# 3. Instalar Serviço via NSSM (Recomendado)
# Verifica se nssm.exe está no path ou na pasta atual
if (Get-Command "nssm" -ErrorAction SilentlyContinue) {
    Write-Host "Instalando serviço via NSSM..."
    nssm install $SERVICE_NAME "$INSTALL_DIR\guardian-agent.exe"
    nssm set $SERVICE_NAME AppDirectory $INSTALL_DIR
    nssm set $SERVICE_NAME AppStdout "$INSTALL_DIR\agent.log"
    nssm set $SERVICE_NAME AppStderr "$INSTALL_DIR\agent.err"
    nssm set $SERVICE_NAME Start SERVICE_AUTO_START
    nssm start $SERVICE_NAME
    Write-Host "Serviço instalado e iniciado com sucesso!"
} else {
    Write-Warning "NSSM não encontrado. Tentando via sc.exe (Pode falhar se o binário não for um Windows Service nativo)..."
    # Nota: Binários PyInstaller simples não respondem ao Service Control Manager, então sc.exe vai dar timeout.
    # NSSM é a solução Enterprise correta aqui.
    Write-Error "ERRO: nssm.exe (Non-Sucking Service Manager) é necessário para instalar este agente como serviço."
    Write-Error "Por favor, baixe o NSSM (https://nssm.cc) e coloque no PATH ou nesta pasta."
}
