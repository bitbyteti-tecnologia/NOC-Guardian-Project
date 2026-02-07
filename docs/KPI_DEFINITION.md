# KPI: Índice de Disponibilidade de Recursos (IDR)

## 1. Definição
O **IDR (Índice de Disponibilidade de Recursos)** é um indicador sintético projetado para medir a "folga" operacional de um servidor ou agente monitorado. Ele identifica o gargalo imediato da infraestrutura, independentemente de qual recurso esteja saturado.

## 2. Fórmula Matemática
O cálculo baseia-se no princípio de "Nivelamento por Baixo" (Worst-Case Scenario). A saúde do sistema é determinada pelo seu recurso mais escasso.

```math
IDR = 100 - MAX(CPU_USAGE%, RAM_USAGE%, DISK_USAGE%)
```

### Exemplo Prático
- **Cenário A:** CPU 10%, RAM 20%, Disk 5%.
    - Gargalo: RAM (20%)
    - IDR: 100 - 20 = **80** (Saudável)
- **Cenário B:** CPU 95%, RAM 40%, Disk 10%.
    - Gargalo: CPU (95%)
    - IDR: 100 - 95 = **5** (Crítico)

## 3. Escala de Classificação
| Faixa de IDR | Status | Descrição | Ação Recomendada |
| :--- | :--- | :--- | :--- |
| **30 a 100** | ✅ HEALTHY | Operação normal com folga. | Monitoramento passivo. |
| **10 a 29** | ⚠️ WARNING | Recurso principal sob stress (>70%). | Investigar processos ou planejar upgrade. |
| **0 a 9** | 🚨 CRITICAL | Saturação iminente (>90%). | Intervenção imediata necessária. |

## 4. Implementação
O script de simulação e cálculo encontra-se em: `scripts/kpi_simulator.py`.
Este KPI é calculado na borda (Edge) ou na Central para gerar alertas proativos antes da falha total do serviço.
