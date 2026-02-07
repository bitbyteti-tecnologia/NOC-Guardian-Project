import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, XOctagon } from 'lucide-react';

export const AlertPanel = ({ alerts }) => {
  if (alerts.length === 0) {
    return (
      <div className="backdrop-blur-md bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-500 h-full shadow-xl relative overflow-hidden group">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.05),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
        <div className="p-6 rounded-full bg-emerald-500/5 border border-emerald-500/10 mb-6 shadow-[0_0_20px_rgba(16,185,129,0.1)] group-hover:scale-110 transition-transform duration-500">
            <CheckCircle className="h-16 w-16 text-emerald-500 drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
        </div>
        <p className="font-bold text-white text-lg tracking-wide uppercase">No Active Alerts</p>
        <p className="text-xs text-emerald-400 font-mono mt-2 tracking-widest uppercase">All Systems Nominal</p>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-md bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden flex flex-col h-full shadow-xl">
      <div className="p-6 border-b border-slate-800 bg-rose-950/20 flex justify-between items-center relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]"></div>
        <h2 className="text-lg font-bold text-rose-400 flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 animate-pulse" />
          Active Incidents
        </h2>
        <span className="bg-rose-500 text-white text-xs font-bold px-2 py-0.5 rounded shadow-[0_0_10px_rgba(244,63,94,0.5)]">
            {alerts.length}
        </span>
      </div>
      
      <div className="overflow-y-auto max-h-[500px] p-4 space-y-3 custom-scrollbar">
        {alerts.map((alert, idx) => (
          <div key={idx} className="bg-slate-950/50 border border-rose-500/30 p-4 rounded-xl shadow-lg relative overflow-hidden group hover:border-rose-500/60 transition-colors">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20">
                <XOctagon size={40} />
            </div>
            
            <div className="flex justify-between items-start relative z-10">
              <span className="font-mono font-bold text-white text-sm bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                {alert.node_id}
              </span>
              <span className="text-[10px] text-rose-950 bg-rose-500 font-bold uppercase px-2 py-0.5 rounded shadow-[0_0_10px_rgba(244,63,94,0.4)]">
                {alert.status}
              </span>
            </div>
            
            <p className="text-sm text-slate-300 mt-3 font-medium leading-relaxed">
                {alert.message}
            </p>
            
            <div className="text-xs text-slate-500 mt-4 flex justify-between items-center pt-3 border-t border-slate-800/50">
               <span className="uppercase tracking-wider text-[10px]">Detected</span>
               <span className="font-mono text-rose-400">
                   {new Date(alert.last_seen * 1000).toLocaleTimeString()}
               </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
