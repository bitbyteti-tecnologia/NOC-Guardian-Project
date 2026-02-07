import React from 'react';
import { Network } from 'lucide-react';

export default function NetworkTrafficCard() {
  return (
    <div className="card-glow p-5 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <Network size={48} className="text-[rgb(59,130,246)]" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Network Traffic</h3>
      <div className="text-3xl font-bold text-white mb-1 drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]">-- Mbps</div>
      <div className="text-slate-500 text-xs">Traffic monitoring initialized</div>
    </div>
  );
}
