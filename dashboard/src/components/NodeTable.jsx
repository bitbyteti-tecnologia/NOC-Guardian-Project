import React from "react";
import { MoreHorizontal, HardDrive, Cpu, Zap } from "lucide-react";

export default function NodeTable({ nodes }) {
    const getStatusBadge = (status) => {
        const styles = {
            HEALTHY: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]",
            WARNING: "bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.2)]",
            CRITICAL: "bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.2)]"
        };
        
        const dots = {
            HEALTHY: "bg-emerald-400",
            WARNING: "bg-amber-400",
            CRITICAL: "bg-rose-400"
        };

        const currentStyle = styles[status] || styles.CRITICAL;
        const currentDot = dots[status] || dots.CRITICAL;

        return (
            <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${currentStyle}`}>
                <span className={`relative flex h-2 w-2`}>
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${currentDot}`}></span>
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${currentDot}`}></span>
                </span>
                {status}
            </span>
        );
    };

    return (
        <div className="backdrop-blur-md bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative">
            {/* Glossy overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>

            <div className="p-6 border-b border-slate-800 flex justify-between items-center relative z-10">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="w-1 h-6 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)]"></span>
                    Infrastructure Nodes
                </h2>
                <div className="text-xs text-slate-500 font-mono bg-slate-950/50 px-3 py-1 rounded-lg border border-slate-800">
                    {nodes.length} MONITORED ASSETS
                </div>
            </div>

            <div className="overflow-x-auto relative z-10">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800/50 bg-slate-900/50">
                            <th className="p-4 font-semibold pl-6">Node Identifier</th>
                            <th className="p-4 font-semibold text-center">Status</th>
                            <th className="p-4 font-semibold">Resources (CPU / RAM / Disk)</th>
                            <th className="p-4 font-semibold text-center">IDR</th>
                            <th className="p-4 font-semibold">Last Seen</th>
                            <th className="p-4 font-semibold text-right pr-6">Action</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-800/50">
                        {nodes.map((n) => (
                            <tr key={n.node_id} className="group hover:bg-slate-800/30 transition-colors duration-300">
                                <td className="p-4 pl-6">
                                    <div className="flex flex-col">
                                        <span className="font-bold text-slate-200 group-hover:text-blue-400 transition-colors">{n.node_id}</span>
                                        <span className="text-xs text-slate-500">v{n.version || '1.0.0'}</span>
                                    </div>
                                </td>
                                <td className="p-4 text-center">
                                    {getStatusBadge(n.status)}
                                </td>
                                <td className="p-4">
                                    <div className="flex items-center gap-4 text-xs text-slate-400">
                                        <div className="flex items-center gap-1" title="CPU">
                                            <Cpu size={14} className="text-blue-400" />
                                            <span>{n.cpu}%</span>
                                        </div>
                                        <div className="flex items-center gap-1" title="RAM">
                                            <Zap size={14} className="text-purple-400" />
                                            <span>{n.ram}%</span>
                                        </div>
                                        <div className="flex items-center gap-1" title="Disk">
                                            <HardDrive size={14} className="text-slate-400" />
                                            <span>{n.disk}%</span>
                                        </div>
                                    </div>
                                </td>
                                <td className="p-4 text-center">
                                    <span className={`font-mono font-bold ${n.idr < 10 ? 'text-rose-400' : 'text-slate-300'}`}>
                                        {n.idr.toFixed(1)}
                                    </span>
                                </td>
                                <td className="p-4 text-slate-400 text-xs font-mono">
                                    {n.last_seen ? new Date(n.last_seen).toLocaleTimeString() : '-'}
                                </td>
                                <td className="p-4 text-right pr-6">
                                    <button className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-all">
                                        <MoreHorizontal size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
