import asyncio
import os
import json
import asyncpg
from datetime import datetime

# DB Config from docker-compose or defaults
DB_USER = os.getenv("POSTGRES_USER", "guardian")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "guardian_pass")
DB_NAME = os.getenv("POSTGRES_DB", "guardian_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

async def audit_last_payload():
    print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}...")
    try:
        dsn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        conn = await asyncpg.connect(dsn)
        
        # Query for the last event of type AGENT_INGEST_RECEIVED
        row = await conn.fetchrow("""
            SELECT time, event_type, node_id, details, tenant_id
            FROM events
            WHERE event_type = 'AGENT_INGEST_RECEIVED'
            ORDER BY time DESC
            LIMIT 1;
        """)
        
        if row:
            print("\n=== PAYLOAD ENCONTRADO ===")
            print(f"Time: {row['time']}")
            print(f"Tenant: {row['tenant_id']}")
            print(f"Agent ID: {row['node_id']}")
            
            payload = json.loads(row['details'])
            print("\n--- JSON Payload ---")
            print(json.dumps(payload, indent=2))
            
            return payload
        else:
            print("\n[!] Nenhum evento AGENT_INGEST_RECEIVED encontrado.")
            return None
            
        await conn.close()
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao conectar ou consultar banco: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(audit_last_payload())
