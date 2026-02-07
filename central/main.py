# ==============================================================================
# NOC - Guardian Central API
# ==============================================================================
# Este arquivo é o ponto de entrada principal para a API do Guardian Central (Cloud).
# Ele utiliza o framework FastAPI para criar endpoints RESTful de alta performance.
#
# A arquitetura segue o padrão de "Inteligência Distribuída", onde este componente
# atua como o cérebro central, recebendo dados dos NODEs (Edge Proxies) e
# servindo o Dashboard Multi-Tenant.
# ==============================================================================

import shutil
from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from typing import Dict, Optional
import os
import base64
import json
import time
import uuid
import asyncio
import logging
import sys
import hashlib
import traceback
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from database import db

# Configuração de Logs (JSON Format friendly for Docker)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("guardian-central")

# Constantes de Versão
APP_VERSION = "1.4.1-debug"

# Inicialização da aplicação FastAPI
# Title: Nome do sistema exibido na documentação automática (Swagger UI)
# Version: Versão atual da API
app = FastAPI(title="NOC - Guardian Central", version=APP_VERSION)
CENTRAL_TOKEN = os.getenv("CENTRAL_TOKEN")
TELEMETRY_MAX_BYTES = int(os.getenv("TELEMETRY_MAX_BYTES", "1048576"))
# Chave de Criptografia Global (Deve ser 32 bytes em HEX)
GUARDIAN_SECRET_KEY = os.getenv("GUARDIAN_SECRET_KEY")
GUARDIAN_ENV = os.getenv("GUARDIAN_ENV", "production")

# Métricas Internas (Self-Monitoring)
INTERNAL_METRICS = {
    "db_write_failures": 0,
    "last_db_error": None,
    "uptime_start": time.time()
}

@app.on_event("startup")
async def startup_event():
    logger.info(f"Guardian Central Starting...")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Environment: {GUARDIAN_ENV}")
    
    # Inicializa conexão com banco de dados
    await db.connect()
    
    # Log de Segurança (Diagnóstico de Chaves)
    if GUARDIAN_SECRET_KEY:
        try:
            key_bytes = bytes.fromhex(GUARDIAN_SECRET_KEY)
            if len(key_bytes) != 32:
                logger.critical(f"[SECURITY FATAL] GUARDIAN_SECRET_KEY tem {len(key_bytes)} bytes. DEVE ter 32 bytes (64 hex chars)!")
                logger.critical("A Criptografia falhará. Verifique o arquivo .env ou docker-compose.yml.")
            else:
                key_hash = hashlib.sha256(GUARDIAN_SECRET_KEY.encode()).hexdigest()[:8]
                logger.info(f"[SECURITY DEBUG] GUARDIAN_SECRET_KEY Hash: {key_hash}... (Length OK: 32 bytes)")
        except ValueError:
            logger.critical("[SECURITY FATAL] GUARDIAN_SECRET_KEY não é uma string HEX válida!")
    else:
        logger.critical("[SECURITY ERROR] GUARDIAN_SECRET_KEY não definida!")

    logger.info(f"Default Tenant: default")
    logger.info(f"System Ready for Ingestion")

@app.get("/debug/ping")
async def debug_ping():
    return {
        "status": "ok", 
        "version": APP_VERSION,
        "env": GUARDIAN_ENV,
        "key_configured": bool(GUARDIAN_SECRET_KEY)
    }

# ==============================================================================
# Endpoint para Dashboard: Status dos Nodes
# ==============================================================================
@app.get("/api/nodes/status")
async def get_nodes_status():
    """
    Retorna o status consolidado de todos os nodes baseado na última telemetria.
    Nunca deve retornar 'Node not found'.
    """

    try:
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT ON (node_id)
                    node_id,
                    timestamp,
                    payload
                FROM telemetry
                ORDER BY node_id, timestamp DESC
            """)

        result = []

        for row in rows:
            payload = row["payload"]

            # Garantir dict
            if isinstance(payload, str):
                payload = json.loads(payload)

            system_health = payload.get("system_health", {})

            cpu = float(system_health.get("cpu_usage", 0))
            ram = float(system_health.get("memory_usage", 0))
            disk = float(system_health.get("disk_usage", 0))

            max_usage = max(cpu, ram, disk)
            idr = 100 - max_usage

            if idr >= 30:
                status = "HEALTHY"
            elif idr >= 10:
                status = "WARNING"
            else:
                status = "CRITICAL"

            result.append({
                "node_id": row["node_id"],
                "last_seen": row["timestamp"].isoformat(),
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "idr": round(idr, 2),
                "status": status
            })

        # IMPORTANTE: se não houver dados, retornar lista vazia
        return result

    except Exception as e:
        logger.error(f"[API ERROR] /api/nodes/status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if not GUARDIAN_SECRET_KEY:
    # AVISO: Em produção, isso deve impedir o startup. 
    # Aqui permitimos, mas o endpoint falhará se chamado.
    logger.warning("GUARDIAN_SECRET_KEY não definida! A descriptografia falhará.")

# Armazenamento em memória do registro e estado dos NODEs
# NODES_REGISTRY armazena metadados completos (UUID, IP, Versão, Status)
NODES_REGISTRY = {}
# NODES_STATUS mantido para compatibilidade rápida, mas sincronizado com REGISTRY
NODES_STATUS = {}
# Estrutura de Alertas (Alert Engine)
ALERTS = []
# Estrutura de Eventos (Event Log - Auditoria)
EVENTS = []
EVENTS_MAX_SIZE = 5000

# ==============================================================================
# Multi-Tenant Helpers & Guardrails
# ==============================================================================
# Cache em memória de tenants válidos para evitar query no DB a cada request.
# Formato: {tenant_id: status}
TENANTS_CACHE = {"default": "ACTIVE"}
TENANTS_CACHE_TTL = 0 # Timestamp de expiração
CACHE_DURATION = 60 # Atualiza a cada 60s se falhar

def get_tenant_key(tenant_id: str, node_id: str) -> str:
    """Gera a chave composta para o Registry (Isolamento Lógico)."""
    return f"{tenant_id}:{node_id}"

async def resolve_and_validate_tenant(
    x_tenant_id: Optional[str] = None,
    x_api_key: Optional[str] = None
) -> str:
    """
    Normaliza e valida o Tenant ID recebido.
    Guardrail de Segurança: Garante que o tenant existe e está ativo.
    Prioridade:
    1. API Key (X-API-Key) -> Resolve tenant associado
    2. Tenant ID explícito (X-Tenant-ID)
    3. Default
    """
    global TENANTS_CACHE, TENANTS_CACHE_TTL
    
    tenant_id = None

    # 1. Resolução via API Key (Alta Prioridade)
    if x_api_key:
        tenant_id = await db.validate_api_key(x_api_key)
        if not tenant_id:
            logger.warning(f"[SECURITY] API Key inválida ou revogada.")
            raise HTTPException(status_code=401, detail="Invalid or Revoked API Key")
        # Se válido, tenant_id já está resolvido e confiável.
    
    # 2. Resolução via Header Explícito (Fallback)
    elif x_tenant_id:
        tenant_id = x_tenant_id.strip().lower()
    
    # 3. Default (Último recurso)
    else:
        tenant_id = "default"

    # Validação Final do Tenant Resolvido (Guardrail de Status)
    if not tenant_id:
        tenant_id = "default"
        
    # Fast Path (Cache Hit)
    if tenant_id in TENANTS_CACHE:
        if TENANTS_CACHE[tenant_id] == "ACTIVE":
            return tenant_id
        else:
            logger.warning(f"[SECURITY] Acesso negado a tenant desativado: {tenant_id}")
            raise HTTPException(status_code=403, detail="Tenant Disabled")

    # Slow Path (Cache Miss / Refresh)
    tenant_data = await db.get_tenant(tenant_id)
    
    if tenant_data:
        TENANTS_CACHE[tenant_id] = tenant_data["status"]
        if tenant_data["status"] == "ACTIVE":
            return tenant_id
        else:
            raise HTTPException(status_code=403, detail="Tenant Disabled")
    else:
        # Tenant não existe
        logger.warning(f"[SECURITY] Tentativa de acesso a tenant inexistente: {tenant_id}")
        # Se veio via API Key válida mas tenant sumiu, é 403. Se veio via ID, é 403.
        raise HTTPException(status_code=403, detail="Invalid Tenant ID")


# ==============================================================================
# Event Manager (Auditoria & Persistência)
# ==============================================================================
async def log_event(event_type: str, node_id: str, severity: Optional[str], message: str, source: str, tenant_id: str = "default"):
    """
    Registra um evento no sistema de auditoria e persiste em disco e banco.
    """
    try:
        current_time = time.time()
        event_data = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "node_id": node_id,
            "severity": severity,
            "message": message,
            "source": source,
            "occurred_at": current_time,
            "detected_at": current_time,
            "timestamp_iso": datetime.fromtimestamp(current_time).isoformat(),
            "tenant_id": tenant_id
        }
        
        # 1. In-Memory Storage (FIFO)
        EVENTS.insert(0, event_data)
        if len(EVENTS) > EVENTS_MAX_SIZE:
            EVENTS.pop()
            
        # 2. Persistência (Append-Only JSONL)
        # Formato: events-YYYY-MM-DD.log
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"events-{date_str}.log"
        
        # Escreve de forma síncrona simples (append)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data) + "\n")
            
        # 3. Persistência em Banco de Dados (Postgres/Timescale)
        try:
            await db.insert_event(event_data)
        except Exception as db_e:
            INTERNAL_METRICS["db_write_failures"] += 1
            INTERNAL_METRICS["last_db_error"] = str(db_e)
            logger.error(f"[CRITICAL] Falha de persistência DB: {db_e}")
            
    except Exception as e:
        logger.error(f"[EVENT LOG ERROR] Falha ao registrar evento: {e}")

async def trigger_alert(node_id: str, old_status: str, new_status: str, tenant_id: str = "default"):
    """
    Gera um alerta quando há mudança de estado no Node.
    """
    severity = "INFO"
    message = f"Node {node_id} mudou de {old_status} para {new_status}"
    
    if new_status == "OFFLINE":
        severity = "CRITICAL"
        message = f"ALERTA CRÍTICO: Node {node_id} parou de responder!"
    elif new_status == "DEGRADED":
        severity = "WARNING"
        message = f"ALERTA: Node {node_id} está operando com buffer ativo."
    elif old_status == "OFFLINE" and new_status == "ONLINE":
        severity = "INFO"
        message = f"RECUPERAÇÃO: Node {node_id} voltou a responder."
        
    # Gera o Alerta (Conceito: Notificação ativa)
    alert = {
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "timestamp_iso": datetime.now().isoformat(),
        "node_id": node_id,
        "old_status": old_status,
        "new_status": new_status,
        "severity": severity,
        "message": message,
        "source": "HEALTH_ENGINE" if new_status == "OFFLINE" else "HEARTBEAT",
        "tenant_id": tenant_id
    }
    
    ALERTS.insert(0, alert)
    if len(ALERTS) > 1000:
        ALERTS.pop()
        
    logger.info(f"[{tenant_id}][{severity}] {message}")
    
    # Persistência DB
    await db.insert_alert(alert)
    
    # Registra no Event Log (Conceito: Auditoria)
    await log_event(
        event_type="ALERT_GENERATED",
        node_id=node_id,
        severity=severity,
        message=message,
        source=alert["source"],
        tenant_id=tenant_id
    )
    
    # Registra a mudança de estado como evento separado (para rastreabilidade pura)
    await log_event(
        event_type="STATE_CHANGE",
        node_id=node_id,
        severity="INFO",
        message=f"Status alterado de {old_status} para {new_status}",
        source=alert["source"],
        tenant_id=tenant_id
    )


def encrypt_payload(data: Dict) -> str:
    """
    Função auxiliar para criptografar payloads AES-256-GCM (Central -> Node).
    """
    if not GUARDIAN_SECRET_KEY:
        raise Exception("Server Security Configuration Error")

    key = bytes.fromhex(GUARDIAN_SECRET_KEY)
    
    # Preparar dados
    json_str = json.dumps(data)
    data_bytes = json_str.encode('utf-8')
    
    # Nonce único
    nonce = os.urandom(12)
    
    # Criptografar
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
    
    # Concatenar Nonce + Ciphertext
    full_payload = nonce + ciphertext
    
    return base64.b64encode(full_payload).decode('utf-8')

def decrypt_payload(encrypted_b64: str) -> Dict:
    """
    Função auxiliar para descriptografar payloads AES-256-GCM.
    """
    if not GUARDIAN_SECRET_KEY:
         raise Exception("Server Security Configuration Error")

    key = bytes.fromhex(GUARDIAN_SECRET_KEY)
    aesgcm = AESGCM(key)
    full_payload = base64.b64decode(encrypted_b64)

    if len(full_payload) < 28:
            raise ValueError("Payload too short")

    nonce = full_payload[:12]
    ciphertext_with_tag = full_payload[12:]
    
    decrypted_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return json.loads(decrypted_bytes.decode('utf-8'))

# ==============================================================================
# Rota de Health Check
# ==============================================================================
# Função: Verificar se a API Central está online e respondendo.
# Utilizado por: Load Balancers e sistemas de monitoramento externos.
@app.get("/health")
async def health_check() -> dict:
    """
    Retorna o status de saúde da API (Deep Health Check).
    Monitora: DB Connectivity, Disk Space, Write Failures.
    """
    health_status = "running"
    db_status = "unknown"
    disk_usage = "unknown"
    
    # 1. Check DB
    try:
        if db.enabled:
            # Simple ping
            await db.list_tenants_with_stats() # Leitura leve
            db_status = "connected"
        else:
            db_status = "disabled"
    except Exception as e:
        db_status = f"error: {str(e)}"
        health_status = "degraded"
        INTERNAL_METRICS["last_db_error"] = str(e)

    # 2. Check Disk
    try:
        total, used, free = shutil.disk_usage(".")
        disk_usage = {
            "total_gb": round(total / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_free": round((free / total) * 100, 1)
        }
        if disk_usage["percent_free"] < 10: # Alerta se < 10% livre
             health_status = "degraded"
    except Exception:
        pass

    return {
        "status": health_status,
        "service": "Guardian Central",
        "version": APP_VERSION,
        "env": GUARDIAN_ENV,
        "uptime_seconds": int(time.time() - INTERNAL_METRICS["uptime_start"]),
        "components": {
            "database": db_status,
            "disk": disk_usage,
            "internal_errors": INTERNAL_METRICS["db_write_failures"]
        }
    }

# ==============================================================================
# Rota Raiz (Landing)
# ==============================================================================
@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Guardian Central online", "docs": "/docs", "health": "/health"}

# ==============================================================================
# Rota de Registro de NODE
# ==============================================================================
@app.post("/ingest/register")
async def register_node(data: Dict, authorization: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    """
    Endpoint para registro inicial do NODE.
    Gera identidade única e distribui políticas de configuração.
    """
    # Guardrail: Validate Tenant
    tenant_id = await resolve_and_validate_tenant(x_tenant_id, x_api_key)
    
    if CENTRAL_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split(" ", 1)[1]
        if token != CENTRAL_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")

    encrypted_b64 = data.get("payload")

    if not encrypted_b64:
        raise HTTPException(status_code=400, detail="Missing 'payload'")

    try:
        # 1. Descriptografar payload de registro
        reg_data = decrypt_payload(encrypted_b64)
        
        # LOG DE DEBUG (Solicitado na Tarefa 4)
        logger.info(f"[REGISTER DEBUG] Payload recebido (Decrypted): {reg_data}")
        
        node_id = reg_data.get("node_id")
        
        if not node_id:
             raise ValueError("Missing node_id")

        # 2. Gerar UUID interno e Registrar
        node_uuid = str(uuid.uuid4())
        current_time = time.time()
        
        # Chave composta para Multi-Tenancy
        reg_key = get_tenant_key(tenant_id, node_id)
        
        NODES_REGISTRY[reg_key] = {
            "uuid": node_uuid,
            "node_id": node_id,
            "tenant_id": tenant_id,
            "hostname": reg_data.get("hostname"),
            "ip": reg_data.get("ip_address") or reg_data.get("ip"), # Support both
            "os": reg_data.get("os"),
            "arch": reg_data.get("arch"),
            "version": reg_data.get("agent_version") or reg_data.get("version"), # Support both
            "registered_at": current_time,
            "last_seen": current_time,
            "status": "ONLINE",
            "buffer_status": "inactive",
            "heartbeat_interval": 60 # Default
        }
        
        logger.info(f"[REGISTER] NODE registrado com sucesso: {node_id} (Tenant: {tenant_id}) (UUID: {node_uuid})")
        
        # Persistência DB
        await db.upsert_node(NODES_REGISTRY[reg_key])

        # Log Event
        await log_event(
            event_type="NODE_REGISTER",
            node_id=node_id,
            severity="INFO",
            message=f"Novo registro efetuado com UUID {node_uuid}",
            source="REGISTER",
            tenant_id=tenant_id
        )
        
        # 3. Preparar Policy de Resposta
        policy = {
            "node_uuid": node_uuid,
            "collection_interval": 30, # Padrão
            "heartbeat_interval": 60,  # Padrão
            "registered_at": current_time,
            "message": "Welcome to Guardian Network"
        }
        
        # 4. Criptografar Resposta
        encrypted_policy = encrypt_payload(policy)
        
        return {"payload": encrypted_policy}

    except InvalidTag:
        logger.warning(f"[REGISTER SECURITY] Falha na descriptografia (InvalidTag). Verifique se as chaves coincidem.")
        raise HTTPException(status_code=400, detail="Registration Failed: Invalid Signature (Key Mismatch?)")
    except ValueError as ve:
        logger.error(f"[REGISTER ERROR] Erro de Valor: {ve}")
        # Retornar traceback no log do servidor para debug profundo
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Registration Failed: ValueError - {str(ve)}")
    except Exception as e:
        logger.error(f"[REGISTER ERROR] Falha no registro: {e}")
        traceback.print_exc()
        # Forçar string de erro explícita
        error_msg = f"{type(e).__name__}: {str(e)}"
        raise HTTPException(status_code=400, detail=f"Registration Failed: {error_msg}")


# ==============================================================================
# Rota de Ingestão de Dados (Agents Enterprise)
# ==============================================================================
@app.post("/ingest/agent")
async def ingest_agent(data: Dict, x_tenant_id: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    """
    Ingestão de dados de Guardian Agents (Windows/Linux).
    Recebe métricas de hosts individuais sem passar pelo Guardian Node.
    """
    # Guardrail: Validate Tenant via API Key (Mandatory for Agents)
    if not x_api_key:
        # Agents devem usar API Key para autenticação direta
        raise HTTPException(status_code=401, detail="Missing X-API-Key")

    tenant_id = await resolve_and_validate_tenant(x_tenant_id, x_api_key)

    # Validação do Payload
    agent_id = data.get("agent_id") or data.get("hostname")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Missing agent_id or hostname")

    # Logging (Info level, no payload details)
    logger.info(f"[AGENT INGEST] Dados recebidos de {agent_id} (Tenant: {tenant_id})")

    # Persistência (Evento de Auditoria + Dados Básicos)
    # Reutilizamos a tabela de eventos para armazenar a ocorrência
    await log_event(
        event_type="AGENT_INGEST_RECEIVED",
        node_id=agent_id,
        severity="INFO",
        message=f"Agent data received from {data.get('os', 'unknown')}",
        source="AGENT",
        tenant_id=tenant_id
    )

    # Retorno Simples
    return {"status": "received", "agent_id": agent_id, "timestamp": time.time()}


# ==============================================================================
# Rota de Ingestão de Dados (Telemetria Real)
# ==============================================================================
# Função: Receber telemetria enviada pelos Guardian NODEs.
# Segurança: Protegido por Token e Criptografia AES-256.
@app.post("/ingest/telemetry")
async def ingest_telemetry(data: Dict, authorization: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None), request: Request = None):
    """
    Endpoint para recepção de dados de telemetria dos nós remotos.
    Persiste os dados no TimescaleDB (Hypertable).
    """
    # 1. Rate Limiting / Size Limiting
    cl = request.headers.get("content-length") if request else None
    if cl and int(cl) > TELEMETRY_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    # 2. Autenticação (Bearer Token)
    if CENTRAL_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split(" ", 1)[1]
        if token != CENTRAL_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")

    # 3. Validação do Tenant
    # Se o Node não enviar header, assume default. 
    # Idealmente o Node deve enviar o tenant_id autenticado no registro.
    tenant_id = "default"
    if x_tenant_id:
         tenant_id = await resolve_and_validate_tenant(x_tenant_id)

    # 4. Validação da Chave Secreta
    if not GUARDIAN_SECRET_KEY:
         logger.critical("[ERRO CRÍTICO] GUARDIAN_SECRET_KEY não configurada no servidor.")
         raise HTTPException(status_code=500, detail="Server Security Configuration Error")

    # 5. Extração do Payload Criptografado
    encrypted_b64 = data.get("payload")
    if not encrypted_b64:
        raise HTTPException(status_code=400, detail="Missing 'payload' field")

    try:
        # 6. Descriptografia
        telemetry_data = decrypt_payload(encrypted_b64)
        
        # Injeta o tenant_id nos dados para persistência
        telemetry_data["tenant_id"] = tenant_id

        # 7. Persistência (TimescaleDB)
        await db.insert_telemetry(telemetry_data)

        # Log de Sucesso (Debug)
        node_id = telemetry_data.get("node_id", "UNKNOWN")
        logger.debug(f"[INGEST] Dados persistidos para {node_id} (Tenant: {tenant_id})")
        
        return {"status": "received", "bytes_processed": len(encrypted_b64)}

    except InvalidTag:
        logger.warning("[ALERTA DE SEGURANÇA] Falha na descriptografia: Assinatura inválida.")
        raise HTTPException(status_code=400, detail="Decryption Failed")
    except Exception as e:
        logger.error(f"[INGEST ERROR] Falha no processamento: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        raise HTTPException(status_code=400, detail="Decryption Failed: Invalid Signature")
    except Exception as e:
        logger.error(f"[ERRO DE PROCESSAMENTO] {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid Payload Format")

# ==============================================================================
# Rota de Heartbeat (Liveness Check)
# ==============================================================================
@app.post("/ingest/heartbeat")
async def ingest_heartbeat(data: Dict, authorization: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None)):
    """
    Endpoint para recepção de sinais de vida (Heartbeat) dos nós.
    
    Atualiza o status do NODE em memória para monitoramento de disponibilidade.
    """
    # Guardrail: Validate Tenant
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    if CENTRAL_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split(" ", 1)[1]
        if token != CENTRAL_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")

    encrypted_b64 = data.get("payload")

    if not encrypted_b64:
        raise HTTPException(status_code=400, detail="Missing 'payload' field")
        
    try:
        # Descriptografa o heartbeat
        hb_data = decrypt_payload(encrypted_b64)
        
        node_id = hb_data.get("node_id")
        if not node_id:
             raise ValueError("Missing node_id in heartbeat")
             
        # Determina Status
        buffer_status = hb_data.get("buffer_status", "inactive")
        new_status = "DEGRADED" if buffer_status == "active" else "ONLINE"
             
        # Atualiza status em memória (Registry)
        reg_key = get_tenant_key(tenant_id, node_id)
        
        if reg_key in NODES_REGISTRY:
            current_status = NODES_REGISTRY[reg_key].get("status", "UNKNOWN")
            
            # Alert Engine Check (Recovery or Degradation)
            if current_status != new_status:
                await trigger_alert(node_id, current_status, new_status, tenant_id)

            NODES_REGISTRY[reg_key]["last_seen"] = hb_data.get("timestamp")
            NODES_REGISTRY[reg_key]["status"] = new_status
            NODES_REGISTRY[reg_key]["buffer_status"] = buffer_status
            NODES_REGISTRY[reg_key]["version"] = hb_data.get("version")
            NODES_REGISTRY[reg_key]["tenant_id"] = tenant_id # Assegura consistência
            
            # Persistência DB
            await db.upsert_node(NODES_REGISTRY[reg_key])
        else:
            # Fallback se não registrado (ou reiniciou Central)
            # Se não conhecemos, assumimos que acabou de chegar (sem alerta de mudança)
            NODES_REGISTRY[reg_key] = {
                "last_seen": hb_data.get("timestamp"),
                "status": new_status,
                "buffer_status": buffer_status,
                "version": hb_data.get("version"),
                "node_id": node_id,
                "tenant_id": tenant_id,
                "uuid": "unknown-unregistered",
                "heartbeat_interval": 60
            }
            # Persistência DB (Fallback)
            await db.upsert_node(NODES_REGISTRY[reg_key])
        
        # Mantém NODES_STATUS para compatibilidade
        # Nota: NODES_STATUS agora usa a mesma chave composta ou o node_id? 
        # Para evitar quebra, mantemos o acesso por node_id SE possível, mas isso cria conflito.
        # Decisão: NODES_STATUS segue o Registry. Onde for usado, deve-se iterar values() ou usar chave composta.
        NODES_STATUS[reg_key] = NODES_REGISTRY[reg_key]
        
        print(f"[HEARTBEAT] ❤️  Sinal recebido de {node_id} (Tenant: {tenant_id}) (Status: {new_status})")
        return {"status": "alive", "server_time": time.time()} # timestamp
        
    except InvalidTag:
        print(f"[HEARTBEAT ERROR] Assinatura inválida.")
        raise HTTPException(status_code=400, detail="Security Error")
    except Exception as e:
        print(f"[HEARTBEAT ERROR] {e}")
        raise HTTPException(status_code=400, detail="Processing Error")


# ==============================================================================
# Health Engine & Alert Engine (Background Tasks)
# ==============================================================================
async def health_monitor_loop():
    """
    Loop infinito que avalia periodicamente a saúde dos nós.
    """
    print("[HEALTH ENGINE] Monitoramento de nós iniciado.")
    while True:
        try:
            await evaluate_nodes_health()
            await asyncio.sleep(10) # Avalia a cada 10 segundos
        except asyncio.CancelledError:
            print("[HEALTH ENGINE] Monitoramento interrompido.")
            break
        except Exception as e:
            print(f"[HEALTH ENGINE ERROR] {e}")
            await asyncio.sleep(10)

async def evaluate_nodes_health():
    """
    Avalia o estado de todos os nós registrados.
    Detecta nós OFFLINE baseando-se no tempo desde o último heartbeat.
    """
    now = time.time()
    
    # Itera sobre uma cópia dos valores para evitar problemas de concorrência simples
    # Chaves agora são compostas, mas values() continua retornando os dados do node
    for node_data in list(NODES_REGISTRY.values()):
        node_id = node_data.get("node_id")
        tenant_id = node_data.get("tenant_id", "default")
        
        last_seen = node_data.get("last_seen", 0)
        interval = node_data.get("heartbeat_interval", 60)
        current_status = node_data.get("status", "UNKNOWN")
        
        # Tolerância: 3x o intervalo de heartbeat
        # Se intervalo = 60s, offline após 180s sem sinal
        threshold = interval * 3
        
        if now - last_seen > threshold:
            # Se já está OFFLINE, não faz nada
            if current_status != "OFFLINE":
                await trigger_alert(node_id, current_status, "OFFLINE", tenant_id)
                
                # Atualiza no Registry
                reg_key = get_tenant_key(tenant_id, node_id)
                
                # Proteção caso a chave tenha mudado ou sido removida
                if reg_key in NODES_REGISTRY:
                    NODES_REGISTRY[reg_key]["status"] = "OFFLINE"
                    # Persistência DB (Atualiza status)
                    await db.upsert_node(NODES_REGISTRY[reg_key])
                    
                    # Sincroniza Status
                    if reg_key in NODES_STATUS:
                        NODES_STATUS[reg_key]["status"] = "OFFLINE"


@app.on_event("startup")
async def startup_event():
    # Inicia conexão com Banco de Dados
    await db.connect()
    # Inicia a tarefa em background sem bloquear o servidor
    asyncio.create_task(health_monitor_loop())

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()

# ==============================================================================
# Endpoints de Monitoramento (NOC Dashboard)
# ==============================================================================
@app.get("/health/nodes")
async def get_nodes_health(authorization: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna o estado atual de todos os nós registrados (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_nodes = [
        n for n in NODES_REGISTRY.values() 
        if n.get("tenant_id", "default") == tenant_id
    ]
    
    return {
        "count": len(tenant_nodes),
        "nodes": tenant_nodes,
        "tenant_id": tenant_id
    }

@app.get("/health/alerts")
async def get_alerts(limit: int = 50, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna os últimos alertas gerados (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_alerts = [
        a for a in ALERTS 
        if a.get("tenant_id", "default") == tenant_id
    ]
    
    return {
        "count": len(tenant_alerts),
        "alerts": tenant_alerts[:limit],
        "tenant_id": tenant_id
    }

@app.get("/events")
async def get_events(limit: int = 100, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna os últimos eventos do sistema (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_events = [
        e for e in EVENTS 
        if e.get("tenant_id", "default") == tenant_id
    ]
    
    return {
        "count": len(tenant_events),
        "limit": limit,
        "events": tenant_events[:limit],
        "tenant_id": tenant_id
    }

# ==============================================================================
# Observability API (Read-Only)
# ==============================================================================

@app.get("/api/nodes")
async def api_get_nodes(x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna a lista completa de nós registrados e seus estados atuais (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_nodes = [
        n for n in NODES_REGISTRY.values() 
        if n.get("tenant_id", "default") == tenant_id
    ]
    return tenant_nodes

@app.get("/api/nodes/{node_id}")
async def api_get_node_details(node_id: str, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna detalhes de um nó específico.
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    reg_key = get_tenant_key(tenant_id, node_id)
    
    node = NODES_REGISTRY.get(reg_key)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    return node

@app.get("/api/nodes/{node_id}/events")
async def api_get_node_events(node_id: str, limit: int = 50, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna histórico de eventos de um nó específico (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    reg_key = get_tenant_key(tenant_id, node_id)
    if reg_key not in NODES_REGISTRY:
         raise HTTPException(status_code=404, detail="Node not found")
         
    node_events = [
        e for e in EVENTS 
        if e.get("node_id") == node_id and e.get("tenant_id", "default") == tenant_id
    ]
    return node_events[:limit]

@app.get("/api/alerts")
async def api_get_alerts(limit: int = 100, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna histórico geral de alertas (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_alerts = [
        a for a in ALERTS 
        if a.get("tenant_id", "default") == tenant_id
    ]
    return tenant_alerts[:limit]

@app.get("/api/alerts/active")
async def api_get_active_alerts(x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna alertas ativos baseados no estado atual dos nós.
    Considera 'ativo' qualquer nó que não esteja 'ONLINE'.
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    active_issues = []
    # Itera sobre Registry. Filtrar pelo Tenant.
    for key, node_data in NODES_REGISTRY.items():
        if node_data.get("tenant_id", "default") != tenant_id:
            continue
            
        node_id = node_data.get("node_id")
        status = node_data.get("status", "UNKNOWN")
        
        if status != "ONLINE":
            # Tenta encontrar o último alerta gerado para este nó para enriquecer o contexto
            related_alert = next((
                a for a in ALERTS 
                if a["node_id"] == node_id and a["new_status"] == status and a.get("tenant_id", "default") == tenant_id
            ), None)
            
            issue = {
                "node_id": node_id,
                "status": status,
                "severity": "CRITICAL" if status == "OFFLINE" else "WARNING",
                "last_seen": node_data.get("last_seen"),
                "message": related_alert["message"] if related_alert else f"Node is {status}"
            }
            active_issues.append(issue)
    return active_issues

@app.get("/api/timeline")
async def api_get_timeline(limit: int = 100, x_tenant_id: Optional[str] = Header(None)):
    """
    Retorna a linha do tempo completa de eventos do sistema (Filtrado por Tenant).
    """
    tenant_id = await resolve_and_validate_tenant(x_tenant_id)
    
    tenant_events = [
        e for e in EVENTS 
        if e.get("tenant_id", "default") == tenant_id
    ]
    return tenant_events[:limit]



# ==============================================================================
# Control Plane API (Admin)
# ==============================================================================
@app.get("/api/tenants")
async def api_list_tenants():
    """
    Lista todos os tenants registrados e estatísticas básicas.
    Endpoint administrativo (Control Plane).
    """
    # Em produção, este endpoint exigiria autenticação de superadmin.
    # Por enquanto, é público/interno.
    tenants = await db.list_tenants_with_stats()
    return tenants

@app.post("/api/tenants/{tenant_id}/keys")
async def api_create_tenant_key(tenant_id: str):
    """
    Gera uma nova API Key para o tenant especificado.
    Retorna a chave APENAS UMA VEZ.
    """
    # Validar se tenant existe
    tenant = await db.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    key_id, raw_key = await db.create_api_key(tenant_id)
    
    if not key_id:
        raise HTTPException(status_code=500, detail="Failed to create API Key")
        
    return {
        "tenant_id": tenant_id,
        "key_id": key_id,
        "api_key": raw_key,
        "warning": "This key will NOT be shown again. Save it securely."
    }

# ==============================================================================
# Ponto de Entrada para Execução Direta
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor Uvicorn na porta 8000
    # Host 0.0.0.0 permite acesso externo (necessário em containers Docker)
    uvicorn.run(app, host="0.0.0.0", port=8000)
