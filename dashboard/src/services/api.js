// Centralized API Client
const API_BASE = '/api';
const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'default';

const headers = {
  'Content-Type': 'application/json',
  'X-Tenant-ID': TENANT_ID
};

export const api = {
  // Nodes
  getNodes: async () => {
    const res = await fetch(`${API_BASE}/nodes`, { headers });
    if (!res.ok) throw new Error('Failed to fetch nodes');
    return res.json();
  },
  
  getNodeDetails: async (id) => {
    const res = await fetch(`${API_BASE}/nodes/${id}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch node details');
    return res.json();
  },
  
  getNodeEvents: async (id, limit = 50) => {
    const res = await fetch(`${API_BASE}/nodes/${id}/events?limit=${limit}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch node events');
    return res.json();
  },
  
  // Alerts
  getActiveAlerts: async () => {
    const res = await fetch(`${API_BASE}/alerts/active`, { headers });
    if (!res.ok) throw new Error('Failed to fetch active alerts');
    return res.json();
  },
  
  // Timeline
  getTimeline: async (limit = 100) => {
    const res = await fetch(`${API_BASE}/timeline?limit=${limit}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return res.json();
  }
};
