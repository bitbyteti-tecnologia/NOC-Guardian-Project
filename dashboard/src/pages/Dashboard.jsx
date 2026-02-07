import React, { useEffect, useState } from 'react';
import { getNodes } from '../services/api';
import StatusGrid from '../components/StatusGrid';
import NodeTable from '../components/NodeTable';
import { GlobalTimeline } from '../components/Timeline';
import { AlertPanel } from '../components/ActiveAlerts';
import Logo from '../components/Logo';
import Header from '../components/Header';
import { Clock, Bell, Menu } from 'lucide-react';

export default function Dashboard({ toggleSidebar }) {
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
        <div className="flex-1 min-h-screen relative overflow-y-auto custom-scrollbar flex flex-col ml-0 lg:ml-20 pt-16 transition-all duration-300">
             {/* Dynamic Background */}
             <div className="fixed inset-0 w-full h-full bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.15),_transparent_50%)] -z-20 pointer-events-none"></div>
             <div className="fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 -z-10 pointer-events-none brightness-50 contrast-150"></div>

            {/* Fixed Header */}
            <Header toggleSidebar={toggleSidebar} metrics={metrics} currentTime={currentTime} />

            <div className="w-full px-4 sm:px-6 lg:px-8 flex flex-col gap-4 md:gap-6 lg:gap-8 mx-auto py-6">
                
                {/* 2. HERO CENTRAL */}
                <div className="relative mb-6 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 p-6 sm:p-8 lg:p-10 shadow-2xl shadow-cyan-500/10">
                    <div className="relative z-10 flex flex-col items-center justify-center gap-4">
                        <div className="scale-100 md:scale-125 mb-2 drop-shadow-[0_0_25px_rgba(56,189,248,0.3)] animate-pulse-slow">
                            <Logo />
                        </div>
                        <div className="space-y-2 text-center">
                            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white tracking-tight drop-shadow-[0_0_15px_rgba(56,189,248,0.3)]">
                                Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#38bdf8] to-[#10b981]">NOC Guardian</span>
                            </h1>
                            <p className="text-slate-400 mt-2 text-sm md:text-base tracking-wide font-light max-w-3xl mx-auto leading-relaxed hidden sm:block">
                                Monitoring, analyzing and correcting your infrastructure in real time
                            </p>
                        </div>
                    </div>
                </div>

                {/* 3. GRID DE STATUS */}
                <StatusGrid metrics={metrics} />

                {/* 4. MAIN CONTENT SPLIT */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                    
                    {/* Left Column (2/3 on Desktop) */}
                    <div className="xl:col-span-2 flex flex-col gap-4 md:gap-6">
                        {/* Infrastructure Nodes Table */}
                        <NodeTable nodes={nodes} />
                        
                        {/* Global Timeline */}
                        <div className="h-[400px]">
                            <GlobalTimeline events={events} />
                        </div>
                    </div>

                    {/* Right Column (1/3 on Desktop) */}
                    <div className="xl:col-span-1 h-full min-h-[500px]">
                        {/* Alert Panel - Sticky on Desktop */}
                        <div className="xl:sticky xl:top-28 h-auto xl:h-[calc(100vh-140px)]">
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
