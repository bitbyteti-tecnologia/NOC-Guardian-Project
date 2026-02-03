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
import random

# Simulação de configuração local
NODE_ID = "NODE-CLIENT-001"
CENTRAL_URL = "https://api.guardian-central.com/ingest"

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
    print(f"[COLETA] Métricas obtidas em {metrics['timestamp']}")
    return metrics

def encrypt_payload(data):
    """
    Realiza o 'Data Scrubbing' e Criptografia.
    
    Args:
        data (dict): Dados em texto claro.
        
    Returns:
        str: Payload simulado criptografado (base64 mock).
    """
    # [REGRA DE OURO]: Dados sensíveis nunca devem trafegar em texto claro.
    # Em produção: Implementar AES-256-GCM.
    json_str = json.dumps(data)
    
    # Simulação de criptografia (apenas para exemplo estrutural)
    encrypted_mock = f"ENC:{len(json_str)}:{hash(json_str)}"
    
    return encrypted_mock

def main_loop():
    """
    Loop principal do serviço NODE.
    Executa ciclicamente a coleta e envio de dados.
    """
    print(f"Iniciando Guardian NODE {NODE_ID}...")
    
    while True:
        try:
            # 1. Coleta
            raw_data = collect_metrics()
            
            # 2. Processamento e Segurança (Data Scrubbing)
            secure_payload = encrypt_payload(raw_data)
            
            # 3. Envio (Outbound Only)
            # O NODE sempre inicia a conexão, evitando portas abertas no Firewall (Inbound).
            print(f"[TUNNEL] Enviando payload seguro para {CENTRAL_URL}...")
            # requests.post(CENTRAL_URL, json={"payload": secure_payload}) # Exemplo real
            
            # Aguarda o próximo ciclo de coleta (ex: 60 segundos)
            time.sleep(5) 
            
        except KeyboardInterrupt:
            print("Parando serviço NODE...")
            break
        except Exception as e:
            print(f"Erro no ciclo de monitoramento: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
