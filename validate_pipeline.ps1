# Script de Validação e KPI - NOC Guardian
# Executar na raiz do projeto onde está o docker-compose.yml

$ErrorActionPreference = "Continue"

function Get-Timestamp {
    return Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

Write-Host "=================================================="
Write-Host " RELATÓRIO DE VALIDAÇÃO NOC GUARDIAN"
Write-Host " Data: $(Get-Timestamp)"
Write-Host "=================================================="
Write-Host ""

# 1. Validar Ingestão no Banco
Write-Host "## 1. VALIDAÇÃO DE INGESTÃO"
Write-Host "Tentando conectar ao banco via Docker..."

$check_cmd = "docker compose exec -T db psql -U guardian guardian_db -t -c ""SELECT count(*) FROM telemetry;"""
$count = Invoke-Expression $check_cmd 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA] Não foi possível conectar ao container do banco."
    Write-Host "Verifique se o Docker está rodando e se os serviços estão ativos."
    exit 1
}

$count = $count.Trim()
if ([int]$count -gt 0) {
    Write-Host "[SUCESSO] Dados detectados no banco. Total de registros: $count"
    $ingestion_status = "FUNCIONANDO"
} else {
    Write-Host "[AVISO] Tabela telemetry vazia."
    $ingestion_status = "SEM DADOS"
    exit 1
}

# 2. Analisar Payload Real
Write-Host ""
Write-Host "## 2. ANÁLISE DE PAYLOAD"
$json_cmd = "docker compose exec -T db psql -U guardian guardian_db -t -c ""SELECT payload FROM telemetry ORDER BY timestamp DESC LIMIT 1;"""
$json_str = Invoke-Expression $json_cmd
$json_str = $json_str.Trim()

if (-not $json_str) {
    Write-Host "[ERRO] Falha ao recuperar payload."
    exit 1
}

try {
    $data = $json_str | ConvertFrom-Json
    Write-Host "Node ID: $($data.node_id)"
    Write-Host "Timestamp (Epoch): $($data.timestamp)"
    
    $cpu = $data.system_health.cpu_usage
    $ram = $data.system_health.memory_usage
    $disk = $data.system_health.disk_usage

    Write-Host "Métricas Recebidas:"
    Write-Host " - CPU: $cpu %"
    Write-Host " - RAM: $ram %"
    
    if ($null -eq $disk) {
        Write-Host " - DISK: NÃO ENCONTRADO (Falha de Coleta)"
        $disk = 0
        $missing_disk = $true
    } else {
        Write-Host " - DISK: $disk %"
        $missing_disk = $false
    }

} catch {
    Write-Host "[ERRO] JSON inválido ou estrutura inesperada."
    Write-Host "Raw: $json_str"
    exit 1
}

# 3. Calcular KPI (IDR)
Write-Host ""
Write-Host "## 3. CÁLCULO DE KPI (IDR)"

$max_usage = $cpu
if ($ram -gt $max_usage) { $max_usage = $ram }
if ($disk -gt $max_usage) { $max_usage = $disk }

$idr = 100 - $max_usage
Write-Host "MAX_USAGE: $max_usage %"
Write-Host "IDR Calculado: $idr"

$status = "UNKNOWN"
if ($idr -ge 30) {
    $status = "HEALTHY"
    Write-Host "Classificação: HEALTHY (Verde)" -ForegroundColor Green
} elseif ($idr -ge 10) {
    $status = "WARNING"
    Write-Host "Classificação: WARNING (Amarelo)" -ForegroundColor Yellow
} else {
    $status = "CRITICAL"
    Write-Host "Classificação: CRITICAL (Vermelho)" -ForegroundColor Red
}

# 4. Conclusão
Write-Host ""
Write-Host "## 4. CONCLUSÃO"
Write-Host "Pipeline Node -> Central -> Database: $ingestion_status"
if ($missing_disk) {
    Write-Host "OBSERVAÇÃO: A métrica 'disk_usage' está ausente no payload."
    Write-Host "Isso afeta a precisão do IDR se o disco for o gargalo."
    Write-Host "Recomendação: Implementar coleta de disco no collector.py."
} else {
    Write-Host "Todas as métricas esperadas foram recebidas."
}
Write-Host "=================================================="
