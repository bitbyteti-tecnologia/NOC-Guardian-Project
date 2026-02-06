# Documentação dos Guardian Agents Enterprise

Os Guardian Agents são componentes leves, outbound-only, projetados para serem executados como serviços em servidores Windows e Linux. Eles coletam métricas de infraestrutura e as enviam de forma segura para o Guardian NODE ou Central.

## Arquitetura e Segurança

*   **Linguagem:** Python 3 (Single Codebase).
*   **Comunicação:** HTTP/1.1 via POST (JSON).
*   **Segurança:**
    *   Autenticação via **API Key** (Tenant Isolation).
    *   Comunicação criptografada (HTTPS recomendado no Load Balancer/Proxy).
    *   O Agente NÃO aceita conexões de entrada (No listening ports).
    *   O Agente NÃO armazena dados localmente (apenas buffer em memória RAM volátil).
*   **Resiliência:**
    *   Timeouts curtos para evitar travamento.
    *   Reinício automático via Systemd (Linux) ou Windows Service Recovery.
    *   Log local rotacionado pelo sistema operacional.

---

## 🖥️ Instalação no Windows

### Pré-requisitos
*   Python 3.8+ instalado (apenas para build).
*   Acesso Administrativo.
*   Ferramenta **NSSM** (Non-Sucking Service Manager) para gerenciamento do serviço.

### Passo 1: Build do Executável
O Agente é distribuído como um executável único (`.exe`) sem dependências externas de runtime.

1.  Abra o PowerShell como Admin.
2.  Navegue até a pasta `agents/windows`.
3.  Execute o build:
    ```powershell
    .\build_exe.ps1
    ```
    Isso gerará a pasta `agents/windows/installer` contendo `guardian-agent.exe` e `config.yaml`.

### Passo 2: Instalação do Serviço
1.  Copie a pasta `installer` para o servidor de destino (ex: `C:\Temp\Installer`).
2.  Edite o arquivo `config.yaml` com a **URL do Node** e a **API Key**.
3.  Execute o instalador (requer NSSM no PATH ou na mesma pasta):
    ```powershell
    .\install_service.ps1
    ```
4.  O serviço `GuardianAgent` será criado e iniciado automaticamente.

### Comandos Úteis
*   Parar serviço: `sc stop GuardianAgent`
*   Iniciar serviço: `sc start GuardianAgent`
*   Logs: `C:\GuardianAgent\agent.log`

---

## 🐧 Instalação no Linux

### Pré-requisitos
*   Acesso root (sudo).
*   Python 3 instalado.

### Passo 1: Instalação Automática
1.  Copie a pasta `agents` para o servidor Linux.
2.  Navegue até `agents/linux`.
3.  Dê permissão de execução e rode o script:
    ```bash
    chmod +x install.sh
    sudo ./install.sh
    ```

### Passo 2: Configuração
1.  Edite o arquivo de configuração gerado:
    ```bash
    sudo nano /etc/guardian-agent/config.yaml
    ```
2.  Insira sua `api_key` e ajuste a `node_url`.
3.  Reinicie o serviço para aplicar:
    ```bash
    sudo systemctl restart guardian-agent
    ```

### Comandos Úteis
*   Status: `sudo systemctl status guardian-agent`
*   Logs: `sudo journalctl -u guardian-agent -f`
*   Parar: `sudo systemctl stop guardian-agent`

---

## ⚙️ Configuração (config.yaml)

O arquivo `config.yaml` é o único ponto de configuração do agente.

```yaml
# URL do Guardian NODE (Recomendado) ou Central
node_url: "http://guardian-node:8000"

# Chave de API gerada no Guardian Central (Admin -> Tenants)
api_key: "noc_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Intervalo de coleta (segundos)
collection_interval: 60

# ID do Agente (Opcional - padrão é o hostname)
agent_id: "srv-prod-01"
```

## 🔄 Atualização e Desinstalação

### Atualizar Agente
1.  Substitua o binário (`.exe` no Windows, `.py` no Linux).
2.  Reinicie o serviço.

### Desinstalar (Windows)
```powershell
nssm remove GuardianAgent confirm
Remove-Item -Recurse -Force "C:\GuardianAgent"
```

### Desinstalar (Linux)
```bash
sudo systemctl stop guardian-agent
sudo systemctl disable guardian-agent
sudo rm /etc/systemd/system/guardian-agent.service
sudo rm -rf /opt/guardian-agent
sudo rm -rf /etc/guardian-agent
sudo userdel guardian-agent
```
