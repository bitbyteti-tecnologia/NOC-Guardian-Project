# Script de Backup do PostgreSQL para NOC Guardian
# Executar via Task Scheduler do Windows
# Requer pg_dump no PATH

$DATE = Get-Date -Format "yyyy-MM-dd"
$BACKUP_DIR = "C:\NOC-Guardian-Backups"
$DB_NAME = "noc_guardian"
$DB_USER = "postgres"
$RETENTION_DAYS = 14

# 1. Criar diretório de backup se não existir
if (!(Test-Path -Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
    Write-Host "Diretório de backup criado: $BACKUP_DIR"
}

# 2. Executar Backup (pg_dump)
$BACKUP_FILE = "$BACKUP_DIR\noc_guardian_$DATE.sql"
Write-Host "Iniciando backup para $BACKUP_FILE..."

# Tenta executar pg_dump. Nota: Pode precisar de senha via .pgpass ou variável de ambiente PGPASSWORD configurada no sistema.
try {
    # Exemplo simples assumindo localhost. Ajustar conforme env vars.
    pg_dump -U $DB_USER -h localhost -d $DB_NAME -f $BACKUP_FILE
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Backup concluído com sucesso."
        
        # Compactar para economizar espaço
        Compress-Archive -Path $BACKUP_FILE -DestinationPath "$BACKUP_FILE.zip" -Force
        Remove-Item $BACKUP_FILE
        Write-Host "Backup compactado: $BACKUP_FILE.zip"
    } else {
        Write-Error "Falha no pg_dump. Código de saída: $LASTEXITCODE"
    }
} catch {
    Write-Error "Erro ao executar pg_dump: $_"
}

# 3. Rotação de Backups (Limpeza)
Write-Host "Verificando backups antigos (mais de $RETENTION_DAYS dias)..."
Get-ChildItem -Path $BACKUP_DIR -Filter "noc_guardian_*.zip" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RETENTION_DAYS) } | ForEach-Object {
    Write-Host "Removendo backup antigo: $($_.Name)"
    Remove-Item $_.FullName
}

Write-Host "Processo de backup finalizado."
