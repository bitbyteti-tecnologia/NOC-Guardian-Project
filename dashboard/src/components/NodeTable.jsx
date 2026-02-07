import React from "react";
import { MoreHorizontal, HardDrive, Cpu, Zap } from "lucide-react";

export default function NodeTable({ nodes }) {
    const getStatusBadge = (status) => {
        const config = {
            HEALTHY: { color: "#10b981", bg: "rgba(16,185,129,0.1)", label: "HEALTHY" },
            WARNING: { color: "#f59e0b", bg: "rgba(245,158,11,0.1)", label: "WARNING" },
            CRITICAL: { color: "#ef4444", bg: "rgba(239,68,68,0.1)", label: "CRITICAL" }
        };

        const style = config[status] || config.CRITICAL;

        return (
            <span 
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider transition-all duration-300 hover:shadow-[0_0_10px_currentColor]"
                style={{ 
                    color: style.color, 
                    backgroundColor: style.bg, 
                    borderColor: `${style.color}40`,
                    boxShadow: `0 0 10px ${style.color}10`
                }}
            >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: style.color }}></span>
                  <span className="relative inline-flex rounded-full h-2 w-2" style={{ backgroundColor: style.color }}></span>
                </span>
                {status}
            </span>
        );
    };

    const ProgressBar = ({ value, color }) => (
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div 
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${value}%`, backgroundColor: color, boxShadow: `0 0 5px ${color}` }}
            ></div>
        </div>
    );

    return (
        <div className="bg-[#0b1220] border rounded-2xl overflow-hidden shadow-2xl relative" style={{ borderColor: 'rgba(59,130,246,0.15)' }}>
            {/* Glossy overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>

            <div className="p-6 border-b border-slate-800/50 flex justify-between items-center relative z-10 bg-slate-900/20">
                <h2 className="text-lg font-bold text-white flex items-center gap-3">
                    <span className="w-1 h-6 bg-[#38bdf8] rounded-full shadow-[0_0_10px_rgba(56,189,248,0.8)]"></span>
                    Infrastructure Nodes
                </h2>
                <div className="text-xs text-[#38bdf8] font-mono bg-[#38bdf8]/10 px-3 py-1 rounded-lg border border-[#38bdf8]/20">
                    {nodes.length} MONITORED ASSETS
                </div>
            </div>

            <div className="overflow-x-auto relative z-10 custom-scrollbar">
                <table className="w-full min-w-[700px] text-left border-collapse">
                    <thead>
                        <tr className="text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800/50 bg-slate-900/50">
                            <th className="p-4 font-semibold pl-6">Node Identifier</th>
                            <th className="p-4 font-semibold text-center">Status</th>
                            <th className="p-4 font-semibold w-1/3">Resources (CPU / RAM / Disk)</th>
                            <th className="p-4 font-semibold text-center hidden md:table-cell">IDR</th>
                            <th className="p-4 font-semibold hidden md:table-cell">Last Seen</th>
                            <th className="p-4 font-semibold text-right pr-6">Action</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-800/30">
                        {nodes.map((n) => {
                            // Mock resource values if missing
                            const cpu = n.cpu || Math.floor(Math.random() * 60) + 10;
                            const ram = n.ram || Math.floor(Math.random() * 70) + 20;
                            const disk = n.disk || Math.floor(Math.random() * 40) + 30;

                            return (
                                <tr key={n.node_id} className="group hover:bg-slate-800/30 transition-colors duration-300">
                                    <td className="p-4 pl-6">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-slate-200 group-hover:text-[#38bdf8] transition-colors font-mono">{n.node_id}</span>
                                            <span className="text-xs text-slate-500">v{n.version || '1.0.0'}</span>
                                        </div>
                                    </td>
                                    <td className="p-4 text-center">
                                        {getStatusBadge(n.status)}
                                    </td>
                                    <td className="p-4">
                                        <div className="flex flex-col gap-2">
                                            <div className="flex items-center gap-3 text-xs text-slate-400">
                                                <div className="w-8 flex justify-end">CPU</div>
                                                <ProgressBar value={cpu} color="#38bdf8" />
                                                <div className="w-8">{cpu}%</div>
                                            </div>
                                            <div className="flex items-center gap-3 text-xs text-slate-400">
                                                <div className="w-8 flex justify-end">RAM</div>
                                                <ProgressBar value={ram} color="#a855f7" />
                                                <div className="w-8">{ram}%</div>
                                            </div>
                                            <div className="flex items-center gap-3 text-xs text-slate-400">
                                                <div className="w-8 flex justify-end">DISK</div>
                                                <ProgressBar value={disk} color="#10b981" />
                                                <div className="w-8">{disk}%</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="p-4 text-center hidden md:table-cell">
                                        <span className={`font-mono font-bold ${n.idr < 10 ? 'text-[#ef4444]' : 'text-slate-300'}`}>
                                            {n.idr ? n.idr.toFixed(1) : '0.0'}
                                        </span>
                                    </td>
                                    <td className="p-4 text-slate-400 text-xs font-mono hidden md:table-cell">
                                        {n.last_seen ? new Date(n.last_seen).toLocaleTimeString() : '-'}
                                    </td>
                                    <td className="p-4 text-right pr-6">
                                        <button className="p-2 hover:bg-[#38bdf8]/10 rounded-lg text-slate-400 hover:text-[#38bdf8] transition-all">
                                            <MoreHorizontal size={18} />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                {nodes.length === 0 && (
                    <div className="p-12 text-center text-slate-500">
                        No nodes connected. Waiting for telemetry...
                    </div>
                )}
            </div>
        </div>
    );
}
