#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Guardian Agent Enterprise (Windows/Linux)
# Copyright (c) 2024 NOC Guardian Project

import os
import sys
import time
import json
import yaml
import socket
import psutil
import requests
import platform
import logging
import uuid
from datetime import datetime

# Configuração de Logging (Stdout apenas - Serviço cuida do arquivo/rotação)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("GuardianAgent")

class GuardianAgent:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.node_url = self.config.get("node_url", "http://localhost:8000")
        self.api_key = self.config.get("api_key")
        self.interval = self.config.get("collection_interval", 60)
        self.agent_id = self.config.get("agent_id") or socket.gethostname()
        self.os_type = platform.system()
        
        if not self.api_key:
            logger.critical("API Key não configurada! Encerrando.")
            sys.exit(1)

        # Dados estáticos do Host
        self.host_info = {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
        }
        
        logger.info(f"Guardian Agent iniciado. ID: {self.agent_id} | OS: {self.os_type}")
        logger.info(f"Target NODE: {self.node_url}")

    def _load_config(self, path):
        # Procura config no diretório atual ou /etc/guardian-agent (Linux) ou C:\GuardianAgent (Windows)
        search_paths = [
            path,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), path),
            "/etc/guardian-agent/config.yaml",
            "C:\\GuardianAgent\\config.yaml"
        ]
        
        for p in search_paths:
            if os.path.exists(p):
                try:
                    with open(p, 'r') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    logger.error(f"Erro ao ler config {p}: {e}")
        
        logger.critical("Arquivo config.yaml não encontrado!")
        sys.exit(1)

    def collect_metrics(self):
        """Coleta métricas de sistema (CPU, RAM, Disco, Rede)."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            mem = psutil.virtual_memory()
            
            # Disco (Raiz)
            disk_path = 'C:\\' if self.os_type == 'Windows' else '/'
            disk = psutil.disk_usage(disk_path)
            
            # Rede (Bytes I/O)
            net = psutil.net_io_counters()
            
            # Latência (Simulada via Ping HTTP simples no próprio Node)
            latency_ms = 0
            try:
                t0 = time.time()
                requests.head(self.node_url, timeout=2)
                latency_ms = round((time.time() - t0) * 1000, 2)
            except:
                latency_ms = -1 # Unreachable

            payload = {
                "agent_id": self.agent_id,
                "timestamp": time.time(),
                "timestamp_iso": datetime.now().isoformat(),
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "ram_usage": mem.percent,
                    "ram_free_gb": round(mem.available / (1024**3), 2),
                    "disk_usage": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2),
                    "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
                    "net_recv_mb": round(net.bytes_recv / (1024**2), 2),
                    "latency_ms": latency_ms
                },
                "host_info": self.host_info
            }
            return payload
            
        except Exception as e:
            logger.error(f"Erro na coleta de métricas: {e}")
            return None

    def send_data(self, payload):
        """Envia dados para o Guardian NODE."""
        if not payload: return

        url = f"{self.node_url}/ingest/agent"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "User-Agent": f"GuardianAgent/1.0 ({self.os_type})"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                logger.info(f"Payload enviado com sucesso. Size: {len(str(payload))} bytes.")
            elif response.status_code == 401:
                logger.error("Falha de Autenticação (401). Verifique a API Key.")
            else:
                logger.warning(f"Falha no envio: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            logger.warning("Falha de conexão com o Guardian NODE.")
        except Exception as e:
            logger.error(f"Erro ao enviar dados: {e}")

    def run(self):
        """Loop principal de execução."""
        logger.info("Iniciando loop de coleta...")
        while True:
            try:
                payload = self.collect_metrics()
                self.send_data(payload)
            except Exception as e:
                logger.error(f"Erro inesperado no loop principal: {e}")
            
            time.sleep(self.interval)

if __name__ == "__main__":
    agent = GuardianAgent()
    agent.run()
