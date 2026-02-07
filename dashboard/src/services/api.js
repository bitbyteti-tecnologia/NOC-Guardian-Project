const API_BASE = "/api";

export async function getNodes() {
    const res = await fetch(`${API_BASE}/nodes/status`);
    if (!res.ok) {
        throw new Error("Erro ao buscar status");
    }
    return res.json();
}

// Manter compatibilidade se necessário
export const getNodeStatus = getNodes;
