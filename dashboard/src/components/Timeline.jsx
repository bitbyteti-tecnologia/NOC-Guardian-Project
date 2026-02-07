import React from 'react';
import { Clock, Activity, AlertCircle, Shield, Radio } from 'lucide-react';

export const GlobalTimeline = ({ events }) => {
  const getIcon = (type, severity) => {
    if (severity === 'CRITICAL') return <AlertCircle size={14} />;
    if (type === 'NODE_REGISTER') return <Shield size={14} />;
    if (type === 'HEARTBEAT') return <Activity size={14} />;
    return <Radio size={14} />;
  };

  const getColor = (type, severity) => {
    if (severity === 'CRITICAL') return { text: '#ef4444', border: '#ef4444', bg: 'rgba(239,68,68,0.1)' };
    if (severity === 'WARNING') return { text: '#f59e0b', border: '#f59e0b', bg: 'rgba(245,158,11,0.1)' };
    if (type === 'NODE_REGISTER') return { text: '#38bdf8', border: '#38bdf8', bg: 'rgba(56,189,248,0.1)' };
    return { text: '#94a3b8', border: '#475569', bg: 'rgba(71,85,105,0.1)' };
  };

  return (
    <div className="bg-[#0b1220] border rounded-2xl overflow-hidden shadow-xl h-full flex flex-col relative group" style={{ borderColor: 'rgba(59,130,246,0.15)' }}>
       {/* Glossy overlay */}
       <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none z-0"></div>

      <div className="p-6 border-b border-slate-800/50 flex justify-between items-center bg-slate-900/20 relative z-10">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Clock className="h-5 w-5 text-[#38bdf8]" />
          Global Event Timeline
        </h2>
        <div className="flex gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
        </div>
      </div>
      
      <div className="p-6 relative flex-1 overflow-y-auto custom-scrollbar z-10">
        {/* Vertical Line */}
        <div className="absolute left-[2.25rem] top-6 bottom-6 w-px bg-gradient-to-b from-transparent via-slate-700 to-transparent"></div>

        <div className="space-y-6">
          {events.length === 0 ? (
             <div className="text-center py-10 text-slate-500 italic font-light">
                Awaiting system telemetry...
             </div>
          ) : (
            events.map((event, idx) => {
                const style = getColor(event.event_type, event.severity);
                return (
                <div key={idx} className="relative pl-10 group/item">
                    {/* Dot on Line */}
                    <div 
                        className="absolute left-[0.65rem] top-1.5 w-3 h-3 rounded-full border-2 bg-[#020617] z-10 transition-all duration-300 group-hover/item:scale-125"
                        style={{ borderColor: style.text, boxShadow: `0 0 10px ${style.text}80` }}
                    ></div>

                    <div className="flex flex-col gap-2 p-4 rounded-xl hover:bg-slate-800/30 transition-all border border-transparent hover:border-slate-700/30">
                        <div className="flex justify-between items-start">
                            <span 
                                className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded border shadow-sm"
                                style={{ color: style.text, backgroundColor: style.bg, borderColor: `${style.text}40` }}
                            >
                                {getIcon(event.event_type, event.severity)}
                                {event.event_type}
                            </span>
                            <span className="text-xs text-slate-500 font-mono">
                                {new Date(event.occurred_at * 1000).toLocaleTimeString()}
                            </span>
                        </div>
                        
                        <p className="text-sm text-slate-300 font-medium leading-relaxed">
                            {event.message}
                        </p>
                        
                        <div className="flex items-center gap-3 mt-1 pt-2 border-t border-slate-800/30">
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest">
                                SRC: <span className="text-slate-400">{event.source}</span>
                            </span>
                            {event.node_id && (
                                 <span className="text-[10px] text-[#38bdf8]/70 font-mono">
                                    ID: {event.node_id}
                                 </span>
                            )}
                        </div>
                    </div>
                </div>
            )})
          )}
        </div>
      </div>
    </div>
  );
};
