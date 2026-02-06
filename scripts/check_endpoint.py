import requests

try:
    print("Checking endpoint existence...")
    resp = requests.post("https://noc.bitbyteti.tec.br/ingest/agent", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
