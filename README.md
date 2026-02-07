NOC-Guardian | Observability & Proactivity System

O NOC-Guardian é uma plataforma moderna de Network Operations Center (NOC) baseada em uma arquitetura de Inteligência Distribuída, projetada para ambientes Multi-Tenant, alta segurança e monitoramento proativo.

O sistema elimina limitações de ferramentas legadas ao distribuir coleta, processamento e inteligência de forma segura e escalável.

🧠 Arquitetura de Inteligência Distribuída

O NOC-Guardian opera em três camadas independentes:

Guardian Central (Cloud)

API e Dashboard Multi-Tenant

Banco de dados central

Correlação de eventos e RCA

Orquestração de alertas e automações

Guardian NODE (Edge Proxy)

Coletor inteligente local

Comunicação outbound-only

Criptografia e sanitização de dados

Buffer local para contingência

Envio seguro para a Central

Guardian Agents

Serviços leves em Windows/Linux

Coleta de telemetria

Comunicação com NODE ou Central

🔒 Segurança por Design

Comunicação via TLS 1.3

MTLS suportado

Criptografia AES-256

Zero Trust

Nenhuma porta inbound no cliente

Certificados rotativos

Dados sanitizados antes do envio

🚀 Tecnologias

Frontend: React + Tailwind

Backend: Python + FastAPI

Automação: Ansible

Banco: PostgreSQL + TimeScaleDB

Infra: Docker Multi-Arch

📂 Estrutura do Projeto
central/   -> API, IA e Dashboard
node/      -> Edge Proxy
agents/    -> Agents Windows/Linux
infra/     -> Docker, hardening, deploy

📦 Deploy do Guardian NODE

Baseado em Docker

Compatível com x86-64 e ARM (Raspberry Pi)

Comunicação segura automática

Buffer local em caso de falha de internet

🛡️ Hardening Obrigatório

UFW / Firewall

Fail2Ban

SSH por chave

Root login desabilitado

Kernel hardening

Atualizações automáticas

📊 Interface NOC

Visão Multi-Tenant

Dashboards por cliente

KPIs em tempo real

Topologia de rede

Diagnóstico interativo (Ping / MTR)

📜 Regra de Ouro

Todo código do NOC-Guardian é educacional, documentado e comentado linha por linha, garantindo transparência, manutenção e evolução segura.

## Deploy Produção

Atualizar tudo:
./ops/deploy_prod.sh

Atualizar apenas Dashboard:
./ops/rebuild_dashboard.sh
