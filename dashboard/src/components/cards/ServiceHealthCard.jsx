import React from 'react';
import { Activity } from 'lucide-react';

export default function ServiceHealthCard({ total, healthy, warning, critical }) {
  return (
    <div className="card-glow p-5 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <Activity size={48} className="text-[rgb(0,255,200)]" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Service Health</h3>
      <div className="text-3xl font-bold text-white mb-4 drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]">{total} Nodes</div>
      
      <div className="flex gap-2 text-xs font-semibold">
        <div className="px-2 py-1 rounded bg-[rgba(34,197,94,0.1)] text-[rgb(34,197,94)] border border-[rgba(34,197,94,0.2)] shadow-[0_0_10px_rgba(34,197,94,0.2)]">
          {healthy} HEALTHY
        </div>
        <div className="px-2 py-1 rounded bg-[rgba(234,179,8,0.1)] text-[rgb(234,179,8)] border border-[rgba(234,179,8,0.2)] shadow-[0_0_10px_rgba(234,179,8,0.2)]">
          {warning} WARN
        </div>
        <div className="px-2 py-1 rounded bg-[rgba(239,68,68,0.1)] text-[rgb(239,68,68)] border border-[rgba(239,68,68,0.2)] shadow-[0_0_10px_rgba(239,68,68,0.2)]">
          {critical} CRIT
        </div>
      </div>
    </div>
  );
}
