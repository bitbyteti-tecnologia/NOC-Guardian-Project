import React from 'react';
import { Wifi } from 'lucide-react';

export default function SystemsOnlineCard({ onlineCount }) {
  return (
    <div className="card-glow p-5 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <Wifi size={48} className="text-[rgb(34,197,94)]" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Systems Online</h3>
      <div className="text-3xl font-bold text-[rgb(34,197,94)] mb-1 drop-shadow-[0_0_5px_rgba(34,197,94,0.5)]">{onlineCount}</div>
      <div className="text-slate-500 text-xs">Active in last 60s</div>
    </div>
  );
}
