# ==============================================================================
# NOC - Guardian NODE (Edge Proxy)
# ==============================================================================
# Este script simula o comportamento do Guardian NODE, o coletor inteligente
# que reside na infraestrutura do cliente.
#
# Responsabilidades:
# 1. Coletar dados locais (SNMP, Ping, Agentes).
# 2. Sanitizar e criptografar os dados (Data Scrubbing).
# 3. Estabelecer túnel seguro (Outbound Only) com a Central.
# ==============================================================================

import time
import json
import os
import requests
import random
import base64
import platform
import socket
import logging
import sys
from collections import deque
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("guardian-node")

# Simulação de configuração local
# Obtém configuração via Variáveis de Ambiente (Boas Práticas para Containers)
NODE_ID = os.getenv("NODE_ID", "NODE-CLIENT-001")
CENTRAL_URL = os.getenv("CENTRAL_URL", "https://api.guardian-central.com/ingest/telemetry")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
# Chave de Criptografia Global (Deve ser 32 bytes em HEX)
GUARDIAN_SECRET_KEY = os.getenv("GUARDIAN_SECRET_KEY")

# ==============================================================================
# Buffer Local (Store & Forward)
# ==============================================================================
# Configuração do buffer: Armazena até 100 payloads se a Central estiver offline.
# Política: FIFO (First-In, First-Out). Se encher, descarta o mais antigo.
BUFFER_MAX_SIZE = int(os.getenv("NODE_BUFFER_SIZE", "100"))
local_buffer = deque(maxlen=BUFFER_MAX_SIZE)

NODE_VERSION = "1.2.0-production"
# Variáveis de Controle de Intervalo (Podem ser atualizadas pela Policy)
NODE_HEARTBEAT_INTERVAL = int(os.getenv("NODE_HEARTBEAT_INTERVAL", "60"))
NODE_COLLECTION_INTERVAL = int(os.getenv("NODE_INTERVAL_SECONDS", "30"))
NODE_UUID = None # Será preenchido no registro

# Healthcheck File Path
HEALTH_FILE = "/tmp/guardian_node_health"

def update_health_file():
    """Atualiza o arquivo de healthcheck para o Docker."""
    try:
        with open(HEALTH_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(f"Failed to update health file: {e}")

def collect_metrics():
    """
    Simula a coleta de métricas de rede local.
    
    Realiza varreduras simuladas em dispositivos de rede (Switches, Roteadores).
    Em produção, utilizaria bibliotecas SNMP (pysnmp) e ICMP.
    
    Returns:
        dict: Dicionário contendo as métricas coletadas.
    """
    # Comentário Educacional:
    # Aqui estamos gerando dados aleatórios para demonstrar a estrutura do payload.
    metrics = {
        "timestamp": time.time(),
        "node_id": NODE_ID,
        "network": {
            "latency_ms": random.randint(5, 50), # Latência simulada para o gateway
            "packet_loss": random.uniform(0, 0.5), # Perda de pacotes simulada (%)
            "bandwidth_usage_mbps": random.uniform(10, 100) # Consumo de banda
        },
        "system_health": {
            "cpu_usage": random.randint(10, 80),
            "memory_usage": random.randint(20, 60)
        }
    }
    # Log local para debug
    logger.debug(f"[COLETA] Métricas obtidas em {metrics['timestamp']}")
    return metrics

def encrypt_payload(data):
    """
    Realiza o 'Data Scrubbing' e Criptografia AES-256-GCM.
    
    Esta função implementa a camada de transporte seguro (Secure Communication Layer).
    
    Args:
        data (dict): Dados em texto claro.
        
    Returns:
        str: Payload criptografado em Base64 (Nonce + Ciphertext + Tag).
    """
    if not GUARDIAN_SECRET_KEY:
        raise ValueError("GUARDIAN_SECRET_KEY não definida. Abortando operação insegura.")

    try:
        # Converter chave de Hex para Bytes
        key = bytes.fromhex(GUARDIAN_SECRET_KEY)
        
        # Preparar dados
        json_str = json.dumps(data)
        data_bytes = json_str.encode('utf-8')
        
        # AES-GCM requer um Nonce (Number used ONCE) único por mensagem
        # Recomendação NIST: 12 bytes (96 bits) para GCM
        nonce = os.urandom(12)
        
        # Inicializar cifra
        aesgcm = AESGCM(key)
        
        # Criptografar
        # O método encrypt retorna o ciphertext com a tag de autenticação anexada ao final
        ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
        
        # Concatenar Nonce + Ciphertext (que já inclui a Tag)
        # Necessário enviar o Nonce para que o receptor possa descriptografar
        full_payload = nonce + ciphertext
        
        # Codificar em Base64 para transporte seguro via JSON
        encrypted_b64 = base64.b64encode(full_payload).decode('utf-8')
        
        return encrypted_b64
        
    except Exception as e:
        logger.critical(f"[ERRO CRÍTICO] Falha na criptografia: {e}")
        # Em caso de erro de criptografia, nunca retornar dados parciais ou inseguros
        raise e

def decrypt_payload(encrypted_b64):
    """
    Função auxiliar para descriptografar payloads AES-256-GCM (Central -> Node).
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

def send_to_central(encrypted_payload, endpoint_suffix="ingest/telemetry"):
    """
    Tenta enviar um payload criptografado para a Central.
    
    Args:
        encrypted_payload (str): Payload Base64 criptografado.
        endpoint_suffix (str): Sufixo da URL (ex: 'ingest/telemetry' ou 'ingest/heartbeat').
        
    Returns:
        response object se HTTP 200, None caso contrário.
    """
    try:
        # Reconstrói a URL baseada na CENTRAL_URL configurada (assume que a env var aponta para a raiz ou endpoint padrão)
        # Se CENTRAL_URL for 'http://api.com/ingest/telemetry', extraímos a base.
        # Simplificação: Vamos assumir que CENTRAL_URL é a base ou ajustamos aqui.
        
        # Lógica de fallback robusta:
        base_url = CENTRAL_URL.split("/ingest")[0]
        target_url = f"{base_url}/{endpoint_suffix}"
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}
        # Timeout curto para evitar travamento do loop se a rede estiver instável
        response = requests.post(target_url, json={"payload": encrypted_payload}, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response
        else:
            logger.warning(f"[ERRO HTTP] Central ({endpoint_suffix}) retornou: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"[FALHA DE CONEXÃO] Erro ao conectar em {endpoint_suffix}: {e}")
        return None

def register_node():
    """
    Realiza o registro inicial do NODE na Central.
    Bloqueia o início das operações até obter sucesso e receber a Policy.
    """
    global NODE_UUID, NODE_HEARTBEAT_INTERVAL, NODE_COLLECTION_INTERVAL
    
    print(f"[REGISTER] Iniciando processo de registro para {NODE_ID}...")
    
    # Coleta metadados do host
    reg_payload = {
        "node_id": NODE_ID,
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "arch": platform.machine(),
        "version": NODE_VERSION,
        "timestamp": time.time()
    }
    
    encrypted_reg = encrypt_payload(reg_payload)
    
    response = send_to_central(encrypted_reg, endpoint_suffix="ingest/register")
    
    if response:
        try:
            resp_data = response.json()
            encrypted_policy = resp_data.get("payload")
            
            if not encrypted_policy:
                logger.error("[REGISTER ERROR] Resposta da Central sem payload.")
                return False
                
            # Descriptografa Policy
            policy = decrypt_payload(encrypted_policy)
            
            NODE_UUID = policy.get("node_uuid")
            logger.info(f"[REGISTER] ✅ Registro concluído! UUID atribuído: {NODE_UUID}")
            
            # Aplica Policy
            if "collection_interval" in policy:
                NODE_COLLECTION_INTERVAL = int(policy["collection_interval"])
                logger.info(f"[POLICY] Intervalo de Coleta atualizado: {NODE_COLLECTION_INTERVAL}s")
                
            if "heartbeat_interval" in policy:
                NODE_HEARTBEAT_INTERVAL = int(policy["heartbeat_interval"])
                logger.info(f"[POLICY] Intervalo de Heartbeat atualizado: {NODE_HEARTBEAT_INTERVAL}s")
                
            return True
            
        except Exception as e:
            logger.error(f"[REGISTER ERROR] Falha ao processar resposta de registro: {e}")
            return False
    else:
        logger.warning(f"[REGISTER] ⚠️  Falha ao conectar com a Central. Tentando novamente...")
        return False

def send_heartbeat():
    """
    Envia sinal de vida (Heartbeat) para a Central.
    Não utiliza buffer em caso de falha (Fire-and-Forget).
    """
    try:
        hb_payload = {
            "node_id": NODE_ID,
            "timestamp": time.time(),
            "version": NODE_VERSION,
            "buffer_status": "active" if len(local_buffer) > 0 else "inactive",
            "buffer_size": len(local_buffer)
        }
        
        encrypted_hb = encrypt_payload(hb_payload)
        
        if send_to_central(encrypted_hb, endpoint_suffix="ingest/heartbeat"):
            logger.info(f"[HEARTBEAT] ❤️  Sinal enviado com sucesso.")
        else:
            logger.warning(f"[HEARTBEAT] 💔 Falha no envio (sem buffer).")
            
    except Exception as e:
        logger.error(f"[HEARTBEAT ERROR] {e}")

def flush_buffer():
    """
    Tenta esvaziar o buffer local reenviando os itens armazenados.
    Deve ser chamado quando a conexão com a Central parece estar saudável.
    """
    if not local_buffer:
        return

    logger.info(f"[RETRY] Tentando reenviar {len(local_buffer)} itens do buffer...")
    
    # Tentamos enviar todos os itens acumulados
    # Se falhar no meio, paramos para tentar novamente no próximo ciclo
    # Isso evita perder tempo se a conexão cair novamente
    count = 0
    while local_buffer:
        # Pega o item mais antigo (FIFO) sem remover ainda
        payload = local_buffer[0]
        
        if send_to_central(payload, endpoint_suffix="ingest/telemetry"):
            # Se sucesso, remove do buffer
            local_buffer.popleft()
            count += 1
        else:
            # Se falhou, interrompe o flush e mantém no buffer
            logger.warning(f"[RETRY FALHOU] Parando reenvio. Restam {len(local_buffer)} itens.")
            break
            
    if count > 0:
        logger.info(f"[RETRY SUCESSO] {count} itens reenviados e removidos do buffer.")

def main_loop():
    """
    Loop principal do serviço NODE.
    Executa ciclicamente a coleta e envio de dados, além do heartbeat.
    """
    logger.info(f"Iniciando Guardian NODE {NODE_ID} (v{NODE_VERSION})...")
    
    # ==============================================================================
    # Fase de Registro (Lifecycle: STARTUP)
    # ==============================================================================
    # O Node não deve iniciar coletas até ser registrado e receber a policy.
    while not register_node():
        retry_delay = 10
        logger.warning(f"[REGISTER] Falha ao registrar. Retry em {retry_delay}s...")
        time.sleep(retry_delay)
    
    logger.info(f"Buffer Local Configurado: Máximo {BUFFER_MAX_SIZE} itens (FIFO)")
    
    # Usa variável global atualizada pelo registro
    # collection_interval = int(os.getenv("NODE_INTERVAL_SECONDS", "30")) # REMOVIDO EM FAVOR DA POLICY
    
    last_collection_time = 0
    last_heartbeat_time = 0
    
    while True:
        try:
            # Healthcheck Signal
            update_health_file()

            now = time.time()
            
            # -------------------------------------------------------
            # TAREFA 1: Heartbeat (Prioridade Alta)
            # -------------------------------------------------------
            if now - last_heartbeat_time >= NODE_HEARTBEAT_INTERVAL:
                send_heartbeat()
                last_heartbeat_time = now
            
            # -------------------------------------------------------
            # TAREFA 2: Coleta de Métricas
            # -------------------------------------------------------
            if now - last_collection_time >= NODE_COLLECTION_INTERVAL:
                # 1. Coleta
                raw_data = collect_metrics()
                
                # 2. Processamento e Segurança (Data Scrubbing)
                secure_payload = encrypt_payload(raw_data)
                
                # 3. Envio (Outbound Only) com Buffer Strategy (Store & Forward)
                
                # Se o buffer já tem itens, adicionamos o novo ao final para manter ordem cronológica
                if len(local_buffer) > 0:
                    logger.info(f"[BUFFERING] Adicionando novo item ao buffer (Fila: {len(local_buffer)})")
                    local_buffer.append(secure_payload)
                    # Tenta esvaziar (Store & Forward)
                    flush_buffer()
                    
                else:
                    # Se buffer vazio, tenta envio direto (Fast Path)
                    logger.debug(f"[TUNNEL] Enviando payload seguro para {CENTRAL_URL}...")
                    if send_to_central(secure_payload, endpoint_suffix="ingest/telemetry"):
                        logger.info(f"[SUCESSO] Dado enviado em tempo real.")
                    else:
                        # Falha no envio direto -> Armazena no buffer
                        logger.warning(f"[FALHA] Armazenando no buffer local para reenvio futuro.")
                        local_buffer.append(secure_payload)
                
                last_collection_time = now

            # Tick do Loop (Sleep curto para responsividade)
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Parando serviço NODE...")
            break
        except Exception as e:
            logger.error(f"Erro no ciclo de monitoramento: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
