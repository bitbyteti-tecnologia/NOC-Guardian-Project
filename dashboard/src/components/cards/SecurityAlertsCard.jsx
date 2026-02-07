import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function SecurityAlertsCard({ criticalCount }) {
  return (
    <div className="card-glow p-5 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <ShieldAlert size={48} className="text-[rgb(239,68,68)]" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Security Alerts</h3>
      <div className="text-3xl font-bold text-[rgb(239,68,68)] mb-1 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]">{criticalCount}</div>
      <div className="text-slate-500 text-xs">Critical incidents detected</div>
    </div>
  );
}
