import React from 'react';
import { Clock, Activity, AlertCircle, Shield, Radio } from 'lucide-react';

export const GlobalTimeline = ({ events }) => {
  const getIcon = (type, severity) => {
    if (severity === 'CRITICAL') return <AlertCircle size={16} />;
    if (type === 'NODE_REGISTER') return <Shield size={16} />;
    if (type === 'HEARTBEAT') return <Activity size={16} />;
    return <Radio size={16} />;
  };

  const getColor = (type, severity) => {
    if (severity === 'CRITICAL') return 'text-rose-400 border-rose-500/50 bg-rose-500/10';
    if (severity === 'WARNING') return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
    if (type === 'NODE_REGISTER') return 'text-blue-400 border-blue-500/50 bg-blue-500/10';
    return 'text-slate-400 border-slate-600/50 bg-slate-600/10';
  };

  return (
    <div className="backdrop-blur-md bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-xl h-full flex flex-col">
      <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-400" />
          Global Event Timeline
        </h2>
        <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-slate-700"></span>
            <span className="w-2 h-2 rounded-full bg-slate-700"></span>
            <span className="w-2 h-2 rounded-full bg-slate-700"></span>
        </div>
      </div>
      
      <div className="p-6 relative flex-1 overflow-y-auto custom-scrollbar">
        {/* Vertical Line */}
        <div className="absolute left-[2.25rem] top-6 bottom-6 w-px bg-gradient-to-b from-transparent via-slate-700 to-transparent"></div>

        <div className="space-y-6">
          {events.length === 0 ? (
             <div className="text-center py-10 text-slate-500 italic">
                Awaiting system events...
             </div>
          ) : (
            events.map((event, idx) => (
                <div key={idx} className="relative pl-10 group">
                {/* Dot on Line */}
                <div className={`absolute left-[0.65rem] top-1 w-3 h-3 rounded-full border-2 bg-slate-900 z-10 transition-all duration-300 group-hover:scale-125 ${
                    event.severity === 'CRITICAL' ? 'border-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' : 
                    event.severity === 'WARNING' ? 'border-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 
                    'border-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]'
                }`}></div>

                <div className="flex flex-col gap-1 p-3 rounded-xl hover:bg-slate-800/40 transition-colors border border-transparent hover:border-slate-700/50">
                    <div className="flex justify-between items-start">
                        <span className={`inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getColor(event.event_type, event.severity)}`}>
                            {getIcon(event.event_type, event.severity)}
                            {event.event_type}
                        </span>
                        <span className="text-xs text-slate-500 font-mono">
                            {new Date(event.occurred_at * 1000).toLocaleTimeString()}
                        </span>
                    </div>
                    
                    <p className="text-sm text-slate-300 font-medium mt-1">
                        {event.message}
                    </p>
                    
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest bg-slate-900 px-1 rounded">
                            SRC: {event.source}
                        </span>
                        {event.node_id && (
                             <span className="text-[10px] text-blue-400/80 font-mono">
                                ID: {event.node_id}
                             </span>
                        )}
                    </div>
                </div>
                </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
