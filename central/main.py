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

from fastapi import FastAPI, HTTPException
from typing import Dict

# Inicialização da aplicação FastAPI
# Title: Nome do sistema exibido na documentação automática (Swagger UI)
# Version: Versão atual da API
app = FastAPI(title="NOC - Guardian Central", version="1.0.0")

# ==============================================================================
# Rota de Health Check
# ==============================================================================
# Função: Verificar se a API Central está online e respondendo.
# Utilizado por: Load Balancers e sistemas de monitoramento externos.
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Retorna o status de saúde da API.
    """
    # Retorna um JSON simples indicando status "ok"
    return {"status": "running", "service": "Guardian Central"}

# ==============================================================================
# Rota de Ingestão de Dados (Exemplo)
# ==============================================================================
# Função: Receber telemetria enviada pelos Guardian NODEs.
# Segurança: Em produção, este endpoint deve ser protegido por mTLS e Tokens.
@app.post("/ingest/telemetry")
async def ingest_telemetry(data: Dict):
    """
    Endpoint para recepção de dados de telemetria dos nós remotos.
    
    Args:
        data (Dict): Payload JSON contendo métricas do NODE.
    
    Returns:
        Dict: Confirmação de recebimento.
    """
    # [TODO]: Implementar validação de schema e descriptografia AES-256 aqui.
    # O NODE envia dados criptografados; a Central deve possuir a chave para abrir.
    
    print(f"Recebido payload de telemetria: {data}")
    
    return {"status": "received", "bytes_processed": len(str(data))}

# ==============================================================================
# Ponto de Entrada para Execução Direta
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor Uvicorn na porta 8000
    # Host 0.0.0.0 permite acesso externo (necessário em containers Docker)
    uvicorn.run(app, host="0.0.0.0", port=8000)
