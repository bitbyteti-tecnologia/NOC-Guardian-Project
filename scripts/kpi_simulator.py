import asyncio
import os
import json
import asyncpg

# DB Config
DB_USER = os.getenv("POSTGRES_USER", "guardian")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "guardian_pass")
DB_NAME = os.getenv("POSTGRES_DB", "guardian_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

async def calculate_kpi():
    print(f"Connecting to {DB_HOST}...")
    try:
        dsn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        conn = await asyncpg.connect(dsn)
        
        # Get last payload
        row = await conn.fetchrow("""
            SELECT details, node_id 
            FROM events 
            WHERE event_type = 'AGENT_INGEST_RECEIVED' 
            ORDER BY time DESC 
            LIMIT 1;
        """)
        
        if not row:
            print("Nenhum dado encontrado.")
            return

        payload = json.loads(row['details'])
        metrics = payload.get("metrics", {})
        
        # Extract Metrics
        cpu = metrics.get("cpu_usage", 0)
        ram = metrics.get("ram_usage", 0)
        disk = metrics.get("disk_usage", 0)
        
        print(f"\n--- DADOS REAIS ({row['node_id']}) ---")
        print(f"CPU:  {cpu}%")
        print(f"RAM:  {ram}%")
        print(f"DISK: {disk}%")
        
        # --- KPI CALCULATION ---
        # KPI: Índice de Disponibilidade de Recursos (IDR)
        # Lógica: O recurso mais saturado define o teto da saúde do servidor.
        
        max_saturation = max(cpu, ram, disk)
        idr_score = 100 - max_saturation
        idr_score = max(0, idr_score) # No negative scores
        
        # Classification
        status = "HEALTHY"
        if idr_score < 10: # >90% usage
            status = "CRITICAL"
        elif idr_score < 30: # >70% usage
            status = "WARNING"
            
        print(f"\n--- KPI CALCULADO ---")
        print(f"KPI Nome: Índice de Disponibilidade de Recursos (IDR)")
        print(f"Fórmula:  100 - MAX(CPU, RAM, DISK)")
        print(f"Valor:    {idr_score:.2f}")
        print(f"Status:   {status}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(calculate_kpi())
