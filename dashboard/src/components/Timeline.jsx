import React from 'react';
import { Clock } from 'lucide-react';

export const Timeline = ({ events, title = "Global Timeline" }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Clock className="h-5 w-5 text-slate-400" />
          {title}
        </h2>
      </div>
      <div className="p-4">
        <div className="relative border-l border-slate-700 ml-3 space-y-6">
          {events.map((event, idx) => (
            <div key={idx} className="mb-6 ml-6 relative">
              <span className={`absolute -left-[31px] flex h-4 w-4 items-center justify-center rounded-full ring-4 ring-slate-900 ${
                event.severity === 'CRITICAL' ? 'bg-rose-500' :
                event.severity === 'WARNING' ? 'bg-amber-500' :
                event.event_type === 'NODE_REGISTER' ? 'bg-blue-500' :
                'bg-slate-500'
              }`}></span>
              
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-baseline">
                <h3 className="text-sm font-semibold text-slate-200">
                  {event.event_type.replace(/_/g, ' ')}
                  <span className="ml-2 font-mono text-xs text-slate-500 bg-slate-800 px-1 rounded">
                    {event.node_id}
                  </span>
                </h3>
                <time className="text-xs text-slate-500">
                  {new Date(event.occurred_at * 1000).toLocaleString()}
                </time>
              </div>
              
              <p className="mt-1 text-sm text-slate-400">
                {event.message}
              </p>
              
              <div className="mt-1 flex gap-2">
                 <span className="text-[10px] uppercase text-slate-600 border border-slate-800 px-1 rounded">
                   Source: {event.source}
                 </span>
                 {event.severity && (
                   <span className={`text-[10px] uppercase px-1 rounded font-bold ${
                     event.severity === 'CRITICAL' ? 'text-rose-400 bg-rose-950/30' :
                     event.severity === 'WARNING' ? 'text-amber-400 bg-amber-950/30' :
                     'text-blue-400 bg-blue-950/30'
                   }`}>
                     {event.severity}
                   </span>
                 )}
              </div>
            </div>
          ))}
          {events.length === 0 && (
            <div className="ml-6 text-slate-500 text-sm italic">No recent events found.</div>
          )}
        </div>
      </div>
    </div>
  );
};
