import os
import asyncio
import json
import time
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict, Tuple

# Tenta importar asyncpg, mas não falha o módulo se não existir (para permitir validação de código)
try:
    import asyncpg
except ImportError:
    asyncpg = None

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.enabled = False
        # Lê variáveis de ambiente
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "password")
        self.db_name = os.getenv("POSTGRES_DB", "noc_guardian")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")

    async def connect(self):
        """
        Estabelece conexão com o banco de dados e cria pool.
        """
        if not asyncpg:
            print("[DATABASE] Driver asyncpg não encontrado. Persistência em DB desativada.")
            return

        try:
            dsn = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            self.pool = await asyncpg.create_pool(dsn)
            self.enabled = True
            print(f"[DATABASE] Conectado ao PostgreSQL/TimescaleDB em {self.host}")
            
            # Inicializa Schema
            await self.init_schema()
            
        except Exception as e:
            print(f"[DATABASE ERROR] Falha na conexão: {e}")
            self.enabled = False

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("[DATABASE] Conexão encerrada.")

    async def init_schema(self):
        """
        Cria tabelas e habilita TimescaleDB se necessário.
        """
        if not self.enabled: return

        async with self.pool.acquire() as conn:
            try:
                # 1. Habilitar TimescaleDB (Requer privilégios de superuser ou já instalado)
                # Ignora erro se não tiver permissão, assumindo que DBA já configurou
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                except Exception as e:
                    print(f"[DATABASE WARNING] Não foi possível ativar extensão TimescaleDB: {e}")

                # 2. Tabela TENANTS (Control Plane)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tenants (
                        tenant_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                # Garantir tenant default
                await conn.execute("""
                    INSERT INTO tenants (tenant_id, name, status)
                    VALUES ('default', 'Default Tenant', 'ACTIVE')
                    ON CONFLICT (tenant_id) DO NOTHING;
                """)
                print("[DATABASE] Tabela 'tenants' verificada e tenant 'default' garantido.")

                # 2.1 Tabela API KEYS (Autenticação)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tenant_api_keys (
                        key_id UUID PRIMARY KEY,
                        tenant_id TEXT REFERENCES tenants(tenant_id),
                        api_key_hash TEXT NOT NULL,
                        status TEXT DEFAULT 'ACTIVE',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        last_used_at TIMESTAMPTZ
                    );
                """)
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON tenant_api_keys (api_key_hash);")

                # 3. Tabela NODES
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS nodes (
                        node_id TEXT PRIMARY KEY,
                        uuid TEXT,
                        hostname TEXT,
                        ip TEXT,
                        version TEXT,
                        registered_at TIMESTAMPTZ,
                        last_seen TIMESTAMPTZ,
                        status TEXT,
                        buffer_status TEXT,
                        metadata JSONB,
                        tenant_id TEXT DEFAULT 'default'
                    );
                """)
                # Migração Aditiva: Garantir que a coluna existe (para DB já criado)
                try:
                    await conn.execute("ALTER TABLE nodes ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';")
                except Exception:
                    pass # Coluna já existe ou erro ignorável

                # 4. Tabela ALERTS
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id UUID PRIMARY KEY,
                        time TIMESTAMPTZ NOT NULL,
                        node_id TEXT REFERENCES nodes(node_id),
                        old_status TEXT,
                        new_status TEXT,
                        severity TEXT,
                        message TEXT,
                        source TEXT,
                        tenant_id TEXT DEFAULT 'default'
                    );
                """)
                try:
                    await conn.execute("ALTER TABLE alerts ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';")
                except Exception:
                    pass

                # 5. Tabela EVENTS (Série Temporal)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        time TIMESTAMPTZ NOT NULL,
                        event_type TEXT,
                        node_id TEXT,
                        severity TEXT,
                        message TEXT,
                        source TEXT,
                        details JSONB,
                        tenant_id TEXT DEFAULT 'default'
                    );
                """)
                try:
                    await conn.execute("ALTER TABLE events ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';")
                except Exception:
                    pass


                # 6. Converter EVENTS em Hypertable (TimescaleDB)
                # Verifica se já é hypertable para evitar erro
                is_hypertable = await conn.fetchval("""
                    SELECT count(*) FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = 'events';
                """)
                
                if is_hypertable == 0:
                    try:
                        await conn.execute("SELECT create_hypertable('events', 'time');")
                        print("[DATABASE] Tabela 'events' convertida para Hypertable.")
                    except Exception as e:
                        print(f"[DATABASE WARNING] Falha ao converter para hypertable (pode ser Postgres puro): {e}")

                # 7. Índices de Performance (Aditivos)
                try:
                    # Tenant Aware Indices
                    await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_tenant_time ON events (tenant_id, time DESC);")
                    await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_tenant_severity ON alerts (tenant_id, severity);")
                    await conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_tenant_last_seen ON nodes (tenant_id, last_seen);")
                except Exception as e:
                    print(f"[DATABASE WARNING] Falha ao criar índices: {e}")

            except Exception as e:
                print(f"[DATABASE ERROR] Falha na inicialização do Schema: {e}")

    async def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        """Busca tenant pelo ID."""
        if not self.enabled: return None
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM tenants WHERE tenant_id = $1", tenant_id)
                return dict(row) if row else None
        except Exception as e:
            print(f"[DATABASE ERROR] get_tenant: {e}")
            return None

    async def list_tenants_with_stats(self) -> list:
        """Lista tenants com contagem de nodes."""
        if not self.enabled: return []
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT t.tenant_id, t.name, t.status, COUNT(n.node_id) as node_count
                    FROM tenants t
                    LEFT JOIN nodes n ON t.tenant_id = n.tenant_id
                    GROUP BY t.tenant_id
                """)
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DATABASE ERROR] list_tenants: {e}")
            return []


    async def create_api_key(self, tenant_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Gera uma nova API Key para o tenant.
        Retorna (key_id, raw_api_key). A raw_api_key deve ser mostrada UMA VEZ.
        """
        if not self.enabled: return None, None
        
        # Gerar API Key segura: prefixo 'noc_' + 32 bytes hex
        raw_key = "noc_" + secrets.token_hex(32)
        # Hash SHA-256 para armazenamento
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_id = secrets.uuid.uuid4()

        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tenant_api_keys (key_id, tenant_id, api_key_hash, status)
                    VALUES ($1, $2, $3, 'ACTIVE')
                """, key_id, tenant_id, key_hash)
                return str(key_id), raw_key
        except Exception as e:
            print(f"[DATABASE ERROR] create_api_key: {e}")
            return None, None

    async def validate_api_key(self, raw_key: str) -> Optional[str]:
        """
        Valida uma API Key e retorna o tenant_id associado.
        Atualiza last_used_at se válida.
        """
        if not self.enabled: return None
        
        try:
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    UPDATE tenant_api_keys
                    SET last_used_at = NOW()
                    WHERE api_key_hash = $1 AND status = 'ACTIVE'
                    RETURNING tenant_id
                """, key_hash)
                
                if row:
                    return row['tenant_id']
                return None
        except Exception as e:
            print(f"[DATABASE ERROR] validate_api_key: {e}")
            return None



    async def upsert_node(self, node_data: Dict):
        """
        Insere ou atualiza um Node.
        """
        if not self.enabled: return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO nodes (node_id, uuid, hostname, ip, version, registered_at, last_seen, status, buffer_status, metadata, tenant_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (node_id) DO UPDATE SET
                        last_seen = EXCLUDED.last_seen,
                        status = EXCLUDED.status,
                        buffer_status = EXCLUDED.buffer_status,
                        version = EXCLUDED.version,
                        ip = EXCLUDED.ip,
                        tenant_id = EXCLUDED.tenant_id;
                """,
                node_data.get("node_id"),
                node_data.get("uuid"),
                node_data.get("hostname"),
                node_data.get("ip"),
                node_data.get("version"),
                datetime.fromtimestamp(node_data.get("registered_at", 0)) if node_data.get("registered_at") else None,
                datetime.fromtimestamp(node_data.get("last_seen", 0)) if node_data.get("last_seen") else None,
                node_data.get("status"),
                node_data.get("buffer_status"),
                json.dumps(node_data), # Salva tudo como metadata extra
                node_data.get("tenant_id", "default")
                )
        except Exception as e:
            print(f"[DATABASE ERROR] Falha ao persistir Node: {e}")

    async def insert_alert(self, alert_data: Dict):
        """
        Insere um novo alerta.
        """
        if not self.enabled: return

        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO alerts (id, time, node_id, old_status, new_status, severity, message, source, tenant_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                alert_data.get("id") if isinstance(alert_data.get("id"), str) else str(alert_data.get("id")),
                datetime.fromtimestamp(alert_data.get("timestamp", time.time())),
                alert_data.get("node_id"),
                alert_data.get("old_status"),
                alert_data.get("new_status"),
                alert_data.get("severity"),
                alert_data.get("message"),
                alert_data.get("source"),
                alert_data.get("tenant_id", "default")
                )
        except Exception as e:
            print(f"[DATABASE ERROR] Falha ao persistir Alerta: {e}")

    async def insert_event(self, event_data: Dict):
        """
        Insere um evento na série temporal.
        """
        if not self.enabled: return

        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO events (time, event_type, node_id, severity, message, source, details, tenant_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                datetime.fromtimestamp(event_data.get("occurred_at", time.time())),
                event_data.get("event_type"),
                event_data.get("node_id"),
                event_data.get("severity"),
                event_data.get("message"),
                event_data.get("source"),
                json.dumps(event_data),
                event_data.get("tenant_id", "default")
                )
        except Exception as e:
            print(f"[DATABASE ERROR] Falha ao persistir Evento: {e}")

    async def purge_old_data(self, retention_days_events: int = 90, retention_days_alerts: int = 180):
        """
        Remove dados antigos do banco de dados (Política de Retenção).
        """
        if not self.enabled: return
        
        try:
            print(f"[DATABASE MAINTENANCE] Iniciando limpeza de dados (Eventos > {retention_days_events}d, Alertas > {retention_days_alerts}d)...")
            async with self.pool.acquire() as conn:
                # 1. Limpar Eventos Antigos
                # TimescaleDB tem drop_chunks, mas assumindo Postgres vanilla ou Timescale básico:
                events_res = await conn.execute("""
                    DELETE FROM events 
                    WHERE time < NOW() - INTERVAL '1 day' * $1
                """, retention_days_events)
                
                # 2. Limpar Alertas Antigos
                alerts_res = await conn.execute("""
                    DELETE FROM alerts 
                    WHERE time < NOW() - INTERVAL '1 day' * $1
                """, retention_days_alerts)
                
                print(f"[DATABASE MAINTENANCE] Limpeza concluída. Eventos removidos: {events_res}, Alertas removidos: {alerts_res}")
                
        except Exception as e:
            print(f"[DATABASE MAINTENANCE ERROR] Falha ao limpar dados antigos: {e}")

# Instância global
db = DatabaseManager()
