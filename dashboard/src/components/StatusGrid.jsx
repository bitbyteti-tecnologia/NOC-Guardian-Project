import React from 'react';
import { Server, Activity, AlertTriangle, XCircle } from 'lucide-react';

const StatusCard = ({ title, value, color, icon: Icon, borderColor }) => {
  return (
    <div 
      className="relative overflow-hidden rounded-2xl bg-[#0b1220] border p-6 backdrop-blur-sm group transition-all duration-500 hover:scale-[1.02]"
      style={{ borderColor: 'rgba(59,130,246,0.15)' }}
    >
      {/* Glow Effect */}
      <div 
        className="absolute -right-6 -top-6 h-24 w-24 rounded-full blur-3xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"
        style={{ backgroundColor: color }}
      ></div>
      
      <div className="flex justify-between items-start relative z-10">
        <div>
          <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">{title}</h3>
          <div 
            className="text-4xl font-black text-white tracking-tight"
            style={{ textShadow: `0 0 20px ${color}40` }}
          >
            {value}
          </div>
        </div>
        <div 
          className="p-3 rounded-xl border shadow-lg transition-all duration-300 group-hover:shadow-[0_0_20px_rgba(0,0,0,0.5)]"
          style={{ 
            backgroundColor: `${color}10`, 
            borderColor: `${color}30`,
            color: color,
            boxShadow: `0 0 15px ${color}20`
          }}
        >
          <Icon size={28} />
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full h-1 bg-slate-800/50"></div>
      <div 
        className="absolute bottom-0 left-0 h-1 w-0 group-hover:w-full transition-all duration-1000 ease-out"
        style={{ 
            background: `linear-gradient(90deg, ${color}, transparent)`
        }}
      ></div>
    </div>
  );
};

export default function StatusGrid({ metrics }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <StatusCard 
        title="Total Nodes" 
        value={metrics.totalNodes} 
        color="#38bdf8" // Neon Blue
        icon={Server} 
      />
      <StatusCard 
        title="Systems Online" 
        value={metrics.healthyCount} 
        color="#10b981" // Green
        icon={Activity} 
      />
      <StatusCard 
        title="Degraded" 
        value={metrics.warningCount} 
        color="#f59e0b" // Yellow
        icon={AlertTriangle} 
      />
      <StatusCard 
        title="Offline / Critical" 
        value={metrics.criticalCount} 
        color="#ef4444" // Red
        icon={XCircle} 
      />
    </div>
  );
}
