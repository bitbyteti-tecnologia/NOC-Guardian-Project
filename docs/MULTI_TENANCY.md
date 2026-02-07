# Arquitetura Multi-Tenant NOC Guardian

Este documento descreve a implementação de Multi-Tenancy (Múltiplos Inquilinos) no NOC Guardian.

## Visão Geral

O NOC Guardian utiliza uma arquitetura **Multi-Tenant Lógica** com isolamento no nível de aplicação e banco de dados. Isso permite que uma única instância do Guardian Central atenda múltiplos clientes (tenants) mantendo seus dados segregados.

### Principais Características
- **Isolamento Lógico**: Dados segregados por coluna `tenant_id`.
- **Tenant Default**: Tenant padrão para compatibilidade e fallback.
- **Autenticação Híbrida**: Suporte a API Key segura ou identificação explícita via header.
- **Control Plane**: API administrativa para gestão de tenants e chaves.

## Autenticação e Resolução de Tenant

O sistema suporta dois métodos para identificar o tenant de uma requisição, com a seguinte prioridade:

### 1. Via API Key (Recomendado)
Utiliza o header `X-API-Key`. Este método é mais seguro pois autentica a origem e resolve o tenant automaticamente.

- **Header**: `X-API-Key: noc_xxxxxxxx...`
- **Comportamento**: 
  - O sistema valida o hash da chave no banco.
  - Se válida, o tenant associado é usado.
  - Se inválida, retorna **401 Unauthorized**.
  - A chave tem prioridade sobre o header `X-Tenant-ID`.

### 2. Via Tenant ID Explícito (Legado/Interno)
Utiliza o header `X-Tenant-ID`. Útil para testes ou sistemas internos confiáveis.

- **Header**: `X-Tenant-ID: cliente-x`
- **Comportamento**:
  - O sistema verifica se o tenant existe e está ativo.
  - Se não existir, retorna **403 Forbidden**.

### 3. Fallback (Default)
Se nenhum header for enviado, o sistema assume o tenant `default` para manter compatibilidade com versões anteriores.

---

## Gerenciamento de Chaves (API Keys)

### Segurança
- As chaves são geradas com alta entropia (32 bytes hex).
- **Apenas o hash SHA-256** é armazenado no banco de dados.
- A chave original é exibida **uma única vez** na criação.

### Gerar Nova API Key
Endpoint administrativo para criar uma chave para um tenant.

```bash
curl -X POST http://localhost:8000/api/tenants/{tenant_id}/keys
```

Retorno:
```json
{
  "tenant_id": "cliente-x",
  "key_id": "uuid-...",
  "api_key": "noc_a1b2c3d4...",
  "warning": "This key will NOT be shown again. Save it securely."
}
```

## Estrutura de Dados (Control Plane)

### Tabela `tenants`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `tenant_id` | TEXT (PK) | Identificador único (ex: `cliente-a`, `default`) |
| `name` | TEXT | Nome amigável do cliente |
| `status` | TEXT | Estado do tenant (`ACTIVE`, `DISABLED`) |
| `created_at` | TIMESTAMPTZ | Data de criação |

### Tabela `tenant_api_keys`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `key_id` | UUID (PK) | Identificador da chave |
| `tenant_id` | TEXT (FK) | Tenant proprietário |
| `api_key_hash` | TEXT | Hash SHA-256 da chave |
| `status` | TEXT | `ACTIVE` ou `REVOKED` |
| `last_used_at` | TIMESTAMPTZ | Auditoria de uso |

## Uso da API

### Listar Tenants (Control Plane)
```bash
curl http://localhost:8000/api/tenants
```
Retorno:
```json
[
  {
    "tenant_id": "default",
    "name": "Default Tenant",
    "status": "ACTIVE",
    "node_count": 5
  },
  {
    "tenant_id": "cliente-x",
    "name": "Cliente X Corp",
    "status": "ACTIVE",
    "node_count": 12
  }
]
```

### Consultar Nodes de um Tenant Específico
```bash
curl -H "X-Tenant-ID: cliente-x" http://localhost:8000/api/nodes
```

### Exemplo de Erro (Tenant Inválido)
```bash
curl -H "X-Tenant-ID: nao-existe" http://localhost:8000/api/nodes
```
Retorno: `403 Forbidden: Invalid Tenant ID`

## Isolamento Interno (Registry)

Para evitar conflitos de IDs de Nodes entre tenants (ex: dois clientes com um node chamado "Firewall-01"), o registro interno em memória utiliza chaves compostas:

- Formato: `{tenant_id}:{node_id}`
- Exemplo: `default:router-01`, `cliente-x:router-01`

Todas as operações de Health Check e Alert Engine respeitam esse isolamento.
