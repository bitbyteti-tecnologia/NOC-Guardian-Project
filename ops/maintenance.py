# Script de Manutenção do NOC Guardian
# Executar via Cron ou Task Scheduler
# Função: Limpeza de dados antigos (DB) e Rotação de Logs JSONL

import os
import sys
import asyncio
import glob
import time
import zipfile
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path para importar central
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from central.database import db

# Configurações
RETENTION_EVENTS_DAYS = 90
RETENTION_ALERTS_DAYS = 180
RETENTION_JSONL_DAYS = 7
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

async def run_maintenance():
    print(f"[{datetime.now()}] Iniciando manutenção do NOC Guardian...")
    
    # 1. Limpeza do Banco de Dados
    try:
        await db.connect()
        if db.enabled:
            await db.purge_old_data(RETENTION_EVENTS_DAYS, RETENTION_ALERTS_DAYS)
        else:
            print("[WARN] Banco de dados não conectado. Pulando limpeza de DB.")
    except Exception as e:
        print(f"[ERROR] Falha na manutenção do DB: {e}")
    finally:
        await db.close()

    # 2. Rotação de Logs JSONL (Compressão e Exclusão)
    try:
        # Encontrar arquivos .log antigos
        # Padrão: events-YYYY-MM-DD.log
        log_files = glob.glob(os.path.join(LOG_DIR, "events-*.log"))
        
        cutoff_date = datetime.now() - timedelta(days=RETENTION_JSONL_DAYS)
        
        for log_file in log_files:
            try:
                # Extrair data do nome do arquivo (events-YYYY-MM-DD.log)
                filename = os.path.basename(log_file)
                date_str = filename.replace("events-", "").replace(".log", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    # Compactar
                    zip_name = log_file + ".zip"
                    print(f"[LOG ROTATION] Compactando {filename}...")
                    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(log_file, arcname=filename)
                    
                    # Remover original
                    os.remove(log_file)
                    print(f"[LOG ROTATION] Original removido: {filename}")
                    
                    # (Opcional) Remover zips muito antigos?
                    # Por enquanto, mantemos zips para backup externo (via script backup_db.ps1 ou similar)
                    
            except ValueError:
                continue # Ignora arquivos que não seguem o padrão de data
            except Exception as e:
                print(f"[ERROR] Falha ao rotacionar {log_file}: {e}")
                
    except Exception as e:
        print(f"[ERROR] Falha geral na rotação de logs: {e}")

    print(f"[{datetime.now()}] Manutenção finalizada.")

if __name__ == "__main__":
    asyncio.run(run_maintenance())
