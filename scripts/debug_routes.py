import sys
import os

# Adiciona o diretório raiz ao path para permitir importação
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from central.main import app
    print("=== DIAGNÓSTICO DE ROTAS REGISTRADAS ===")
    print(f"App Title: {app.title}")
    print(f"App Version: {app.version}")
    
    print("\n[ROTAS ENCONTRADAS]")
    found = False
    for route in app.routes:
        methods = ", ".join(route.methods)
        print(f" - {route.path} [{methods}]")
        if route.path == "/ingest/agent":
            found = True
            
    print("\n[RESULTADO DO DIAGNÓSTICO]")
    if found:
        print("✅ O endpoint '/ingest/agent' ESTÁ registrado corretamente no código Python.")
        print("   -> Conclusão: O problema é OPERACIONAL (Docker Image desatualizada).")
    else:
        print("❌ O endpoint '/ingest/agent' NÃO foi encontrado no objeto app.")
        print("   -> Conclusão: O problema é DE CÓDIGO (Erro de sintaxe ou lógica).")

except ImportError as e:
    print(f"Erro ao importar app: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
