# Script de Build do Guardian Agent para Windows
# Requer Python e PyInstaller instalados
# Executar como Admin

$ERROR_ACTION_PREFERENCE = "Stop"

# 1. Instalar dependências
Write-Host "Instalando dependências..."
pip install -r ..\requirements.txt

# 2. Gerar Executável (OneFile)
Write-Host "Compilando Guardian Agent..."
# --noconsole: não abre janela preta (ideal para serviço)
# --onefile: tudo num único .exe
# --name: nome do arquivo de saída
pyinstaller --noconsole --onefile --name "guardian-agent" ..\guardian_agent.py

# 3. Preparar diretório de distribuição
$DIST_DIR = "installer"
if (!(Test-Path $DIST_DIR)) { New-Item -ItemType Directory -Path $DIST_DIR }

Copy-Item "dist\guardian-agent.exe" -Destination $DIST_DIR
Copy-Item "..\config.yaml.example" -Destination "$DIST_DIR\config.yaml"

Write-Host "Build concluído! Arquivos em agents\windows\installer"
Write-Host "Para instalar como serviço, use o script install_service.ps1"
