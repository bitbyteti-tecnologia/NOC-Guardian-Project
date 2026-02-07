# Relatório Técnico de Revisão - NOC Guardian
**Data:** 2026-02-06
**Responsável:** Assistant

## 1. Diagnóstico Crítico: Endpoint `/ingest/agent` Indisponível
**Problema:** O endpoint foi implementado no código (`central/main.py`), mas não aparece na documentação Swagger/OpenAPI em produção.
**Causa Raiz:** O serviço `central` no `docker-compose.yml` não utiliza volumes para mapear o código local (`./central:/app`). Portanto, o container está rodando uma versão "congelada" (stale) da imagem Docker, construída antes da alteração do código.
**Solução:** É obrigatório executar um **rebuild** da imagem para incorporar as mudanças.
> Comando: `docker compose up -d --build central`

## 2. Análise de Build e Docker
### 2.1. Arquivo `.dockerignore`
- **Status:** Ausente (Falha).
- **Impacto:** O contexto de build do Docker está copiando arquivos desnecessários (`.git`, `node_modules`, arquivos temporários), aumentando o tempo de build e o tamanho da imagem, além de riscos de segurança.
- **Ação:** Criado arquivo `.dockerignore` na raiz.

### 2.2. Dockerfile (`central/Dockerfile`)
- **Status:** Correto.
- **Observação:** Utiliza `python:3.9-slim`, boa prática. O comando `COPY . .` é seguro desde que o `.dockerignore` exista.

## 3. Configuração do Docker Compose
- **Credenciais:** As variáveis de ambiente `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc., estão configuradas corretamente no arquivo.
- **Volumes:** O serviço `traefik` persiste certificados em `./letsencrypt`. O serviço `db` usa volume nomeado (implícito). O serviço `central` NÃO tem persistência de código (correto para produção, exige rebuild para deploy).
- **Dependências:** `depends_on: db (service_healthy)` garante que a API só sobe após o banco estar pronto.

## 4. Banco de Dados
- **Status:** Configurado com TimescaleDB.
- **Verificação:** Não foi possível validar o runtime (logs/status real) devido a restrições de permissão no terminal atual (`docker` command not found). Recomenda-se verificar manualmente via `docker logs guardian-db`.

## 5. KPI e Monitoramento
- **KPI Definido:** Índice de Disponibilidade de Recursos (IDR).
- **Documentação:** Criada em `docs/KPI_DEFINITION.md`.
- **Script:** Validado em `scripts/kpi_simulator.py`.

## 6. Próximos Passos (Action Items)
1. [CRÍTICO] Executar script de rebuild (`ops/scripts/rebuild_central.ps1`) no host.
2. Validar se o endpoint aparece em `/docs` após o rebuild.
3. Testar ingestão de dados com o script `scripts/kpi_simulator.py`.
