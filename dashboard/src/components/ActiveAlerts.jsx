import React from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export const ActiveAlerts = ({ alerts }) => {
  if (alerts.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-slate-500 h-full">
        <CheckCircle className="h-12 w-12 text-emerald-500/50 mb-2" />
        <p className="font-medium">No Active Alerts</p>
        <p className="text-xs">All systems nominal</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col h-full">
      <div className="p-4 border-b border-slate-800 bg-rose-950/20">
        <h2 className="text-lg font-semibold text-rose-400 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Active Incidents
        </h2>
      </div>
      <div className="overflow-y-auto max-h-[400px] p-2 space-y-2">
        {alerts.map((alert, idx) => (
          <div key={idx} className="bg-slate-950 border-l-4 border-rose-500 p-3 rounded shadow-sm">
            <div className="flex justify-between items-start">
              <span className="font-bold text-slate-200 text-sm">{alert.node_id}</span>
              <span className="text-xs text-rose-400 font-bold uppercase">{alert.status}</span>
            </div>
            <p className="text-sm text-slate-400 mt-1">{alert.message}</p>
            <div className="text-xs text-slate-600 mt-2 flex justify-between">
               <span>Last seen: {new Date(alert.last_seen * 1000).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
