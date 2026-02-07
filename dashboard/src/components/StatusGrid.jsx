import React from 'react';
import { Server, Activity, AlertTriangle, XCircle } from 'lucide-react';

const StatusCard = ({ title, value, color, icon: Icon, glowColor }) => {
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-slate-900/50 border border-slate-800 p-6 backdrop-blur-sm group hover:border-${color}-500/50 transition-all duration-500`}>
      <div className={`absolute -right-6 -top-6 h-24 w-24 rounded-full bg-${color}-500/10 blur-2xl group-hover:bg-${color}-500/20 transition-all duration-500`}></div>
      
      <div className="flex justify-between items-start relative z-10">
        <div>
          <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">{title}</h3>
          <div className={`text-4xl font-black text-white tracking-tight drop-shadow-[0_0_10px_rgba(${glowColor},0.5)]`}>
            {value}
          </div>
        </div>
        <div className={`p-3 rounded-xl bg-${color}-500/10 border border-${color}-500/20 text-${color}-400 shadow-[0_0_15px_rgba(${glowColor},0.3)]`}>
          <Icon size={28} />
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-slate-700 to-transparent opacity-20"></div>
      <div className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r from-${color}-500 to-${color}-400 w-0 group-hover:w-full transition-all duration-1000 ease-out`}></div>
    </div>
  );
};

export default function StatusGrid({ metrics }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <StatusCard 
        title="Total Nodes" 
        value={metrics.totalNodes} 
        color="blue" 
        glowColor="59,130,246"
        icon={Server} 
      />
      <StatusCard 
        title="Systems Online" 
        value={metrics.healthyCount} 
        color="emerald" 
        glowColor="16,185,129"
        icon={Activity} 
      />
      <StatusCard 
        title="Degraded" 
        value={metrics.warningCount} 
        color="amber" 
        glowColor="245,158,11"
        icon={AlertTriangle} 
      />
      <StatusCard 
        title="Offline / Critical" 
        value={metrics.criticalCount} 
        color="rose" 
        glowColor="244,63,94"
        icon={XCircle} 
      />
    </div>
  );
}
