import React, { useEffect, useState } from 'react';
import { StatCard } from '../components/Layout';
import { NodeList } from '../components/NodeList';
import { ActiveAlerts } from '../components/ActiveAlerts';
import { Timeline } from '../components/Timeline';
import { api } from '../services/api';
import { Server, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

const Dashboard = () => {
  const [nodes, setNodes] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  const fetchData = async () => {
    try {
      const [nodesData, alertsData, timelineData] = await Promise.all([
        api.getNodes(),
        api.getActiveAlerts(),
        api.getTimeline(20)
      ]);
      setNodes(nodesData);
      setAlerts(alertsData);
      setTimeline(timelineData);
      setLastUpdated(Date.now());
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading NOC Dashboard...</div>;

  // Stats Calculation
  const totalNodes = nodes.length;
  const onlineNodes = nodes.filter(n => n.status === 'ONLINE').length;
  const offlineNodes = nodes.filter(n => n.status === 'OFFLINE').length;
  const degradedNodes = nodes.filter(n => n.status === 'DEGRADED').length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Nodes" value={totalNodes} icon={Server} />
        <StatCard title="Online" value={onlineNodes} type="success" icon={CheckCircle} />
        <StatCard title="Degraded" value={degradedNodes} type="warning" icon={Activity} />
        <StatCard title="Offline" value={offlineNodes} type="danger" icon={AlertTriangle} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Nodes List (Span 2) */}
        <div className="lg:col-span-2 space-y-6">
           <NodeList nodes={nodes} />
           <Timeline events={timeline} />
        </div>

        {/* Right Column: Alerts & Status */}
        <div className="space-y-6">
          <ActiveAlerts alerts={alerts} />
          
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs text-slate-500">
             <p>Dashboard updates automatically every 5 seconds.</p>
             <p className="mt-1">Last update: {new Date(lastUpdated).toLocaleTimeString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
