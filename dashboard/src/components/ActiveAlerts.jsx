import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, XOctagon } from 'lucide-react';

export const AlertPanel = ({ alerts }) => {
  if (alerts.length === 0) {
    return (
      <div 
        className="backdrop-blur-md bg-[#0b1220] border rounded-2xl p-6 flex flex-col items-center justify-center text-slate-500 h-full shadow-xl relative overflow-hidden group"
        style={{ borderColor: 'rgba(59,130,246,0.15)' }}
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.05),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
        <div className="p-6 rounded-full bg-[#10b981]/5 border border-[#10b981]/10 mb-6 shadow-[0_0_20px_rgba(16,185,129,0.1)] group-hover:scale-110 transition-transform duration-500 relative">
            <div className="absolute inset-0 rounded-full animate-ping opacity-20 bg-[#10b981]"></div>
            <CheckCircle className="h-16 w-16 text-[#10b981] drop-shadow-[0_0_10px_rgba(16,185,129,0.5)] relative z-10" />
        </div>
        <p className="font-bold text-white text-lg tracking-wide uppercase">No Active Alerts</p>
        <p className="text-xs text-[#10b981] font-mono mt-2 tracking-widest uppercase">All Systems Operational</p>
      </div>
    );
  }

  return (
    <div 
        className="backdrop-blur-md bg-[#0b1220] border rounded-2xl overflow-hidden flex flex-col h-full shadow-xl"
        style={{ borderColor: 'rgba(59,130,246,0.15)' }}
    >
      <div className="p-6 border-b border-slate-800/50 bg-rose-950/10 flex justify-between items-center relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-[#ef4444] shadow-[0_0_10px_rgba(239,68,68,0.8)]"></div>
        <h2 className="text-lg font-bold text-[#ef4444] flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 animate-pulse" />
          Active Incidents
        </h2>
        <span className="bg-[#ef4444] text-white text-xs font-bold px-2 py-0.5 rounded shadow-[0_0_10px_rgba(239,68,68,0.5)]">
            {alerts.length}
        </span>
      </div>
      
      <div className="overflow-y-auto max-h-[500px] p-4 space-y-3 custom-scrollbar">
        {alerts.map((alert, idx) => (
          <div key={idx} className="bg-slate-950/50 border border-rose-500/20 p-4 rounded-xl shadow-lg relative overflow-hidden group hover:border-rose-500/50 transition-colors">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20">
                <XOctagon size={40} className="text-[#ef4444]" />
            </div>
            
            <div className="flex justify-between items-start relative z-10">
              <span className="font-mono font-bold text-white text-sm bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                {alert.node_id || 'SYS'}
              </span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded shadow-sm ${
                  alert.severity === 'CRITICAL' 
                  ? 'text-white bg-[#ef4444] shadow-[0_0_10px_rgba(239,68,68,0.4)]' 
                  : 'text-slate-900 bg-[#f59e0b] shadow-[0_0_10px_rgba(245,158,11,0.4)]'
              }`}>
                {alert.severity}
              </span>
            </div>
            
            <p className="text-sm text-slate-300 mt-3 font-medium leading-relaxed">
                {alert.message}
            </p>
            
            <div className="text-xs text-slate-500 mt-4 flex justify-between items-center pt-3 border-t border-slate-800/50">
               <span className="uppercase tracking-wider text-[10px]">Detected</span>
               <span className="font-mono text-[#ef4444]">
                   {new Date((alert.occurred_at || alert.last_seen || Date.now()/1000) * 1000).toLocaleTimeString()}
               </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
