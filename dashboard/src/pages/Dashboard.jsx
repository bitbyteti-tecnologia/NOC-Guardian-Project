import React, { useEffect, useState } from 'react';
import { getNodes } from '../services/api';
import StatusGrid from '../components/StatusGrid';
import NodeTable from '../components/NodeTable';
import { GlobalTimeline } from '../components/Timeline';
import { AlertPanel } from '../components/ActiveAlerts';
import Logo from '../components/Logo';
import { Clock, ShieldCheck, Bell } from 'lucide-react';

export default function Dashboard() {
    const [nodes, setNodes] = useState([]);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [events, setEvents] = useState([]);
    const [metrics, setMetrics] = useState({
        totalNodes: 0,
        healthyCount: 0,
        warningCount: 0,
        criticalCount: 0,
        averageIDR: 0,
        onlineNodes: 0
    });

    // Mock Event Generator to make the dashboard look alive
    const generateMockEvents = (currentNodes) => {
        const newEvents = [];
        const timestamp = Math.floor(Date.now() / 1000);
        
        // 1. Generate events from critical/warning nodes
        currentNodes.forEach(node => {
            if (node.status === 'CRITICAL') {
                newEvents.push({
                    event_type: 'ALERT',
                    severity: 'CRITICAL',
                    node_id: node.node_id,
                    message: `Critical threshold exceeded for ${node.node_id}`,
                    occurred_at: timestamp,
                    source: 'SYS_MON'
                });
            } else if (node.status === 'WARNING') {
                 newEvents.push({
                    event_type: 'ALERT',
                    severity: 'WARNING',
                    node_id: node.node_id,
                    message: `High resource usage detected`,
                    occurred_at: timestamp - Math.floor(Math.random() * 300),
                    source: 'SYS_MON'
                });
            }
        });

        // 2. Add some generic operational events
        newEvents.push({
            event_type: 'HEARTBEAT',
            severity: 'INFO',
            message: 'Routine system integrity scan completed',
            occurred_at: timestamp - 60,
            source: 'CORE_SVC'
        });

         if (Math.random() > 0.7) {
            newEvents.push({
                event_type: 'NODE_REGISTER',
                severity: 'INFO',
                node_id: `node-${Math.floor(Math.random() * 100)}`,
                message: 'New node registration handshake initiated',
                occurred_at: timestamp - 120,
                source: 'REGISTRY'
            });
        }

        // Sort by time
        return newEvents.sort((a, b) => b.occurred_at - a.occurred_at).slice(0, 10);
    };

    const loadData = async () => {
        try {
            const data = await getNodes();
            setNodes(data);
            calculateMetrics(data);
            setEvents(generateMockEvents(data));
            setLastUpdate(new Date());
        } catch (e) {
            console.error("Failed to load nodes", e);
        }
    };

    const calculateMetrics = (data) => {
        const totalNodes = data.length;
        const healthyCount = data.filter(n => n.status === 'HEALTHY').length;
        const warningCount = data.filter(n => n.status === 'WARNING').length;
        const criticalCount = data.filter(n => n.status === 'CRITICAL').length;
        
        // Average IDR
        const totalIDR = data.reduce((acc, curr) => acc + (curr.idr || 0), 0);
        const averageIDR = totalNodes > 0 ? (totalIDR / totalNodes).toFixed(1) : 0;

        // Online Nodes (seen in last 60s)
        const now = new Date();
        const onlineNodes = data.filter(n => {
            if (!n.last_seen) return false;
            const lastSeen = new Date(n.last_seen);
            const diffSeconds = (now - lastSeen) / 1000;
            return diffSeconds < 60;
        }).length;

        setMetrics({
            totalNodes,
            healthyCount,
            warningCount,
            criticalCount,
            averageIDR,
            onlineNodes
        });
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000); // 5 seconds update
        const clockInterval = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => {
            clearInterval(interval);
            clearInterval(clockInterval);
        };
    }, []);

    // Derive active alerts for the panel (only CRITICAL and WARNING)
    const activeAlerts = events.filter(e => e.severity === 'CRITICAL' || e.severity === 'WARNING');

    return (
        <div className="flex-1 bg-slate-950 min-h-screen relative overflow-y-auto custom-scrollbar flex flex-col">
             {/* Dynamic Background */}
             <div className="fixed inset-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black -z-20 pointer-events-none"></div>
             <div className="fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 -z-10 pointer-events-none brightness-50 contrast-150"></div>

            {/* 1. TOPO (Header Global) */}
            <div className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 shadow-lg px-8 py-4 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Logo size="icon" />
                    <div className="h-6 w-px bg-slate-800 mx-2"></div>
                    <span className="text-slate-400 font-mono text-xs tracking-widest uppercase">Central Command</span>
                </div>
                
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3 px-4 py-1.5 bg-emerald-500/5 border border-emerald-500/20 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                        <div className="relative">
                            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping absolute opacity-75"></div>
                            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full relative shadow-[0_0_5px_rgba(16,185,129,0.8)]"></div>
                        </div>
                        <span className="text-emerald-400 text-xs font-bold tracking-wider uppercase">System Operational</span>
                    </div>

                    <div className="flex items-center gap-3 text-slate-300 font-mono text-sm bg-slate-900 px-4 py-2 rounded-lg border border-slate-800">
                        <Clock size={16} className="text-blue-400" />
                        <span>{currentTime.toLocaleTimeString()}</span>
                    </div>
                    
                    <button className="relative p-2 text-slate-400 hover:text-white transition-colors">
                        <Bell size={20} />
                        {metrics.criticalCount > 0 && (
                            <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-rose-500 rounded-full animate-ping border border-slate-950"></span>
                        )}
                    </button>
                    
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 p-[1px]">
                        <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center">
                             <span className="font-bold text-white">OP</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-8 flex flex-col gap-8 max-w-[1920px] mx-auto w-full">
                
                {/* 2. HERO CENTRAL */}
                <div className="relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900/40 p-12 text-center group">
                    <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2/3 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent blur-sm"></div>
                    
                    <div className="relative z-10 flex flex-col items-center justify-center gap-6">
                        <div className="scale-125 mb-4 drop-shadow-[0_0_25px_rgba(59,130,246,0.3)] animate-pulse-slow">
                            <Logo />
                        </div>
                        <div className="space-y-2">
                            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight">
                                Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">NOC Guardian</span>
                            </h1>
                            <p className="text-slate-400 text-lg tracking-wide font-light max-w-2xl mx-auto">
                                Monitoring, analyzing and protecting your infrastructure with advanced real-time diagnostics.
                            </p>
                        </div>
                    </div>
                </div>

                {/* 3. GRID DE STATUS */}
                <StatusGrid metrics={metrics} />

                {/* 4. MAIN CONTENT SPLIT */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                    
                    {/* Left Column (2/3) */}
                    <div className="xl:col-span-2 flex flex-col gap-8">
                        {/* Infrastructure Nodes Table */}
                        <NodeTable nodes={nodes} />
                        
                        {/* Global Timeline */}
                        <div className="h-[400px]">
                            <GlobalTimeline events={events} />
                        </div>
                    </div>

                    {/* Right Column (1/3) */}
                    <div className="xl:col-span-1 h-full min-h-[500px]">
                        {/* Alert Panel - Sticky if content allows */}
                        <div className="sticky top-28 h-[calc(100vh-140px)]">
                            <AlertPanel alerts={activeAlerts} />
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Footer */}
            <div className="mt-auto py-6 text-center text-slate-600 text-xs uppercase tracking-widest border-t border-slate-900 bg-slate-950">
                NOC Guardian Enterprise • v2.4.0 • Secure Connection
            </div>
        </div>
    );
}
