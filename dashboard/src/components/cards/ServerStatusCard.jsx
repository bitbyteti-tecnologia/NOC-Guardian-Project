import React from 'react';
import { Server } from 'lucide-react';

export default function ServerStatusCard({ averageIDR }) {
  const getStatusColor = (idr) => {
    if (idr >= 30) return 'text-[rgb(34,197,94)] drop-shadow-[0_0_5px_rgba(34,197,94,0.5)]';
    if (idr >= 10) return 'text-[rgb(234,179,8)] drop-shadow-[0_0_5px_rgba(234,179,8,0.5)]';
    return 'text-[rgb(239,68,68)] drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]';
  };

  return (
    <div className="card-glow p-5 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <Server size={48} className="text-[rgb(168,85,247)]" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Server Status (Avg IDR)</h3>
      <div className={`text-3xl font-bold mb-1 ${getStatusColor(averageIDR)}`}>
        {averageIDR}%
      </div>
      <div className="text-slate-500 text-xs">Global Idle Resource Average</div>
    </div>
  );
}
