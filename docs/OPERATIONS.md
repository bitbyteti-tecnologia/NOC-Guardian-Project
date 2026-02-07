# Manual de Operações NOC Guardian

Este documento contém os procedimentos padrão para operação, manutenção e recuperação de desastres do ambiente de produção do NOC Guardian.

## 1. Monitoramento do Sistema (Self-Monitoring)

O NOC Guardian possui um endpoint de saúde detalhado que deve ser monitorado por um sistema externo (ex: Nagios, Zabbix ou Uptime Kuma).

**Endpoint:** `GET /health`
**Exemplo de Resposta:**
```json
{
  "status": "running",
  "uptime_seconds": 12345,
  "components": {
    "database": "connected",
    "disk": {
      "free_gb": 45.2,
      "percent_free": 20.5
    },
    "internal_errors": 0
  }
}
```

**Regras de Alerta:**
- Se `status` != "running" -> **CRÍTICO**
- Se `components.database` != "connected" -> **CRÍTICO**
- Se `components.disk.percent_free` < 10% -> **WARNING**
- Se `components.internal_errors` > 10 -> **WARNING**

---

## 2. Backup e Restore

### Backup Automático
O script de backup deve ser agendado no **Windows Task Scheduler** para rodar diariamente (ex: às 02:00 AM).

- **Script:** `ops/scripts/backup_db.ps1`
- **O que faz:**
  1. Executa `pg_dump` do banco `noc_guardian`.
  2. Compacta o arquivo SQL em ZIP.
  3. Remove backups mais antigos que 14 dias (Rotação).
- **Destino:** `C:\NOC-Guardian-Backups`

### Restore (Recuperação de Desastre)
Para restaurar um backup em caso de falha total:

1. Pare o serviço do Guardian Central.
2. Descompacte o arquivo de backup desejado.
3. Execute o restore via psql:
   ```powershell
   # Atenção: Isso APAGA o banco atual e recria
   dropdb -U postgres noc_guardian
   createdb -U postgres noc_guardian
   psql -U postgres -d noc_guardian -f "C:\NOC-Guardian-Backups\noc_guardian_YYYY-MM-DD.sql"
   ```
4. Reinicie o serviço.

---

## 3. Manutenção e Limpeza (Retenção de Dados)

O script de manutenção deve ser agendado para rodar diariamente ou semanalmente.

- **Script:** `ops/maintenance.py`
- **Comando:** `python ops/maintenance.py`
- **Ações:**
  1. **Banco de Dados:** Remove Eventos > 90 dias e Alertas > 180 dias.
  2. **Logs em Disco:** Compacta e rotaciona arquivos JSONL (`events-*.log`) mais antigos que 7 dias.

---

## 4. Checklist de Deploy

Antes de atualizar a versão em produção:

1. [ ] Verificar status atual em `/health`.
2. [ ] Executar backup manual (`ops/scripts/backup_db.ps1`).
3. [ ] Parar o serviço Python.
4. [ ] Atualizar código (git pull).
5. [ ] Atualizar dependências (`pip install -r requirements.txt`).
6. [ ] Rodar migrações (se houver - o sistema atual usa Auto-Migrate no startup).
7. [ ] Iniciar serviço.
8. [ ] Validar logs de inicialização.
9. [ ] Testar acesso ao Dashboard e recepção de dados de um Node.

## 5. Variáveis de Ambiente Críticas

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUARDIAN_SECRET_KEY` | Chave Mestra de Criptografia (32 bytes hex) | **OBRIGATÓRIO** |
| `POSTGRES_HOST` | Endereço do Banco de Dados | localhost |
| `POSTGRES_PASSWORD` | Senha do Banco | password |
| `TELEMETRY_MAX_BYTES` | Tamanho máximo de payload (Proteção DDoS) | 1048576 (1MB) |

---

## 6. Procedimentos de Emergência

### Disco Cheio
1. Verifique `C:\NOC-Guardian-Backups` e remova arquivos antigos manualmente.
2. Verifique logs JSONL na raiz do projeto e mova para armazenamento frio.
3. Execute `python ops/maintenance.py` manualmente.

### Banco de Dados Travado
1. Reinicie o serviço PostgreSQL.
2. Verifique logs do Postgres.
3. Se corrompido, proceda com o **Restore**.
