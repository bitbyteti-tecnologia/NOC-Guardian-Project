# Guia de Deploy - Guardian Enterprise (Docker)

Este documento descreve o procedimento padrão para deploy, atualização e manutenção do NOC Guardian em ambiente de produção utilizando Docker e Docker Compose.

## 📋 Pré-requisitos

*   **Servidor Linux:** Ubuntu 20.04 LTS ou superior (Recomendado).
*   **Docker Engine:** v20.10+
*   **Docker Compose:** v2.0+
*   **Recursos Mínimos:** 2 vCPU, 4GB RAM, 50GB Disco SSD.
*   **Domínio Configurado:** Apontando para o IP do servidor (ex: `noc.seudominio.com`).

## 📂 Estrutura de Diretórios

A estrutura foi padronizada para facilitar a operação:

```
/opt/noc-guardian/
├── docker-compose.yml      # Orquestração dos serviços
├── .env                    # Variáveis de ambiente (NÃO COMITAR)
├── central/                # Código da API Central
├── node/                   # Código do Node (se rodar local)
├── ops/                    # Scripts de manutenção
└── docs/                   # Documentação
```

## 🚀 Primeira Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/seu-repo/noc-guardian.git /opt/noc-guardian
    cd /opt/noc-guardian
    ```

2.  **Configure o Ambiente:**
    Copie o exemplo e edite com suas credenciais seguras.
    ```bash
    cp .env.example .env
    nano .env
    ```
    *Gere chaves fortes para `GUARDIAN_SECRET_KEY` (32 bytes hex) e `CENTRAL_TOKEN`.*

3.  **Build e Start:**
    ```bash
    docker compose build
    docker compose up -d
    ```

4.  **Verifique a Saúde:**
    ```bash
    docker compose ps
    # Aguarde status "healthy" para central e db
    curl https://noc.seudominio.com/health
    ```

## 🔄 Procedimento de Atualização (Update)

O sistema foi desenhado para atualizações sem downtime perceptível (Rolling Update via Docker).

1.  **Baixe a última versão:**
    ```bash
    cd /opt/noc-guardian
    git pull origin main
    ```

2.  **Reconstrua as Imagens:**
    Garante que as alterações de código (Python) sejam empacotadas.
    ```bash
    docker compose build
    ```

3.  **Aplique as Mudanças:**
    O Docker recriará apenas os containers modificados.
    ```bash
    docker compose up -d
    ```

4.  **Valide o Update:**
    Verifique os logs de inicialização para confirmar a versão.
    ```bash
    docker compose logs -f central --tail=50
    # Procure por: "Guardian Central Starting... Version: X.Y.Z"
    ```

## 🛡️ Rollback (Reversão)

Caso uma atualização apresente falhas críticas:

1.  **Reverta o Código:**
    ```bash
    git checkout <hash-do-commit-anterior>
    # ou
    git checkout v1.3.0  # Se usar tags
    ```

2.  **Reconstrua e Reinicie:**
    ```bash
    docker compose build
    docker compose up -d
    ```

## 📊 Monitoramento e Logs

Os logs são centralizados no stdout/stderr do Docker.

*   **Ver logs em tempo real:**
    ```bash
    docker compose logs -f
    ```
*   **Ver logs de um serviço específico:**
    ```bash
    docker compose logs -f central
    docker compose logs -f node
    docker compose logs -f db
    ```

## 🔧 Manutenção do Banco de Dados

O banco de dados (TimescaleDB) persiste os dados no volume `postgres_data`.

*   **Backup (via Script):**
    Execute o script de backup (dentro ou fora do container).
    ```bash
    docker compose exec db pg_dump -U guardian guardian_db > backup_$(date +%F).sql
    ```

*   **Healthcheck Manual:**
    ```bash
    docker compose exec db pg_isready -U guardian
    ```

## 🌐 Troubleshooting Traefik & SSL

O Traefik gerencia automaticamente os certificados SSL. Se houver problemas:

1.  **Verificar Logs do Traefik:**
    ```bash
    docker compose logs -f traefik
    ```
    *Procure por erros como "Unable to obtain ACME certificate" ou "Challenge failed".*

2.  **Verificar Certificados Armazenados:**
    O arquivo `acme.json` armazena as chaves.
    ```bash
    ls -l letsencrypt/acme.json
    # Deve ter permissão 600 (rw-------)
    ```

3.  **Forçar Renovação:**
    Em casos extremos, apague o `acme.json` e reinicie o Traefik (Cuidado: Rate Limits do Let's Encrypt).
    ```bash
    rm letsencrypt/acme.json
    docker compose restart traefik
    ```
