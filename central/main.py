# ==============================================================================
# NOC - Guardian Central API
# ==============================================================================
from fastapi import FastAPI, HTTPException, Header, Request, Depends, Query
from typing import Dict, Optional, List, Any
import os
import json
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text, select, desc
from sqlalchemy.dialects.postgresql import JSONB

# ==============================================================================
# Configuração de Banco de Dados (Postgres / TimescaleDB)
# ==============================================================================
POSTGRES_USER = os.getenv("POSTGRES_USER", "guardian")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "guardian_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "guardian_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    node_id: Mapped[str] = mapped_column(index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB)

# ==============================================================================
# Ciclo de Vida da Aplicação
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: Aguardar DB e criar tabelas
    # Em produção, usar Alembic para migrações. Aqui, create_all para simplificar.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Tenta converter tabela em hypertable (TimescaleDB)
        # Se falhar (ex: não for Timescale ou já existir), apenas logamos o erro/aviso
        try:
            await conn.execute(text("SELECT create_hypertable('telemetry', 'timestamp', if_not_exists => TRUE);"))
        except Exception as e:
            print(f"Info: Hypertable setup skipped or failed (OK if using standard Postgres): {e}")
    yield
    # Encerramento
    await engine.dispose()

# ==============================================================================
# Inicialização da API
# ==============================================================================
app = FastAPI(title="NOC - Guardian Central", version="1.1.0", lifespan=lifespan)
CENTRAL_TOKEN = os.getenv("CENTRAL_TOKEN")
TELEMETRY_MAX_BYTES = int(os.getenv("TELEMETRY_MAX_BYTES", "1048576"))

# Dependência para obter sessão do DB
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ==============================================================================
# Rotas Básicas
# ==============================================================================
@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "running", "service": "Guardian Central", "database": "connected"}

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Guardian Central online", "docs": "/docs", "health": "/health"}

# ==============================================================================
# Rotas de Ingestão e Leitura
# ==============================================================================
@app.post("/ingest/telemetry")
async def ingest_telemetry(
    data: Dict, 
    authorization: Optional[str] = Header(None), 
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    # 1. Validação de Tamanho (Proteção DoS)
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

    # 3. Persistência
    try:
        # Tenta extrair node_id se estiver visível, senão usa 'encrypted/unknown'
        node_id = data.get("node_id", "unknown_or_encrypted")
        
        telemetry_entry = Telemetry(
            node_id=str(node_id),
            payload=data
        )
        db.add(telemetry_entry)
        await db.commit()
        await db.refresh(telemetry_entry)
        
        return {"status": "received", "id": telemetry_entry.id, "bytes_processed": len(str(data))}
    except Exception as e:
        print(f"Erro ao persistir telemetria: {e}")
        raise HTTPException(status_code=500, detail="Database Error")

@app.get("/telemetry")
async def read_telemetry(
    node_id: Optional[str] = None, 
    limit: int = 100, 
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna os últimos registros de telemetria.
    Útil para o Dashboard (polling ou histórico).
    """
    query = select(Telemetry).order_by(desc(Telemetry.timestamp)).offset(skip).limit(limit)
    if node_id:
        query = query.where(Telemetry.node_id == node_id)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    return entries

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
