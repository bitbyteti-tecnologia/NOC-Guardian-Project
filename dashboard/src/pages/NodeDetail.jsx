import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { StatCard, StatusBadge } from '../components/Layout';
import { Timeline } from '../components/Timeline';
import { ArrowLeft, Server, Cpu, HardDrive, Clock } from 'lucide-react';

const NodeDetail = () => {
  const { id } = useParams();
  const [node, setNode] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const [nodeData, eventsData] = await Promise.all([
        api.getNodeDetails(id),
        api.getNodeEvents(id, 50)
      ]);
      setNode(nodeData);
      setEvents(eventsData);
    } catch (err) {
      setError("Failed to load node data. It might not exist.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [id]);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading Node Details...</div>;
  if (error) return (
    <div className="p-8 text-center">
      <p className="text-rose-400 mb-4">{error}</p>
      <Link to="/" className="text-blue-400 hover:underline">Back to Dashboard</Link>
    </div>
  );

  if (!node) return null;

  return (
    <div className="space-y-6">
      {/* Header / Breadcrumb */}
      <div className="flex items-center gap-4">
        <Link to="/" className="p-2 bg-slate-800 rounded hover:bg-slate-700 transition">
          <ArrowLeft className="h-5 w-5 text-slate-300" />
        </Link>
        <div>
           <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
             {node.hostname || node.node_id}
             <StatusBadge status={node.status} />
           </h1>
           <p className="text-slate-400 text-sm font-mono">{node.node_id}</p>
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
         <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
           <h3 className="text-xs uppercase text-slate-500 font-bold mb-1">IP Address</h3>
           <p className="font-mono text-slate-200">{node.ip}</p>
         </div>
         <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
           <h3 className="text-xs uppercase text-slate-500 font-bold mb-1">Version</h3>
           <p className="text-slate-200">{node.version || 'Unknown'}</p>
         </div>
         <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
           <h3 className="text-xs uppercase text-slate-500 font-bold mb-1">Last Seen</h3>
           <p className="text-slate-200">{new Date(node.last_seen * 1000).toLocaleString()}</p>
         </div>
         <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
           <h3 className="text-xs uppercase text-slate-500 font-bold mb-1">Buffer Status</h3>
           <p className={`font-bold ${node.buffer_status === 'active' ? 'text-amber-400' : 'text-emerald-400'}`}>
             {node.buffer_status === 'active' ? 'ACTIVE (Lagging)' : 'INACTIVE (Real-time)'}
           </p>
         </div>
      </div>

      {/* Events Timeline */}
      <Timeline events={events} title={`Event History for ${node.hostname || node.node_id}`} />
      
      {/* Raw Data (Debug) */}
      <div className="bg-slate-950 border border-slate-900 rounded-lg p-4">
        <h3 className="text-xs uppercase text-slate-600 font-bold mb-2">Raw Metadata</h3>
        <pre className="text-xs text-slate-600 overflow-x-auto font-mono">
          {JSON.stringify(node, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default NodeDetail;
