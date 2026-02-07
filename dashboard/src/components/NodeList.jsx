import React from 'react';
import { StatusBadge } from './Layout';
import { ChevronRight, Server } from 'lucide-react';
import { Link } from 'react-router-dom';

export const NodeList = ({ nodes }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Server className="h-5 w-5 text-blue-400" />
          Infrastructure Nodes
        </h2>
        <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">
          Total: {nodes.length}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
            <tr>
              <th className="px-4 py-3">Node ID</th>
              <th className="px-4 py-3">Hostname</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Last Seen</th>
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {nodes.map((node) => (
              <tr key={node.node_id} className="hover:bg-slate-800/50 transition-colors">
                <td className="px-4 py-3 font-mono text-slate-300">{node.node_id}</td>
                <td className="px-4 py-3 text-slate-400">{node.hostname || '-'}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={node.status} />
                </td>
                <td className="px-4 py-3 text-slate-500">{node.version || 'v?'}</td>
                <td className="px-4 py-3 text-slate-400">
                  {new Date(node.last_seen * 1000).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <Link 
                    to={`/node/${node.node_id}`} 
                    className="text-blue-400 hover:text-blue-300 flex items-center gap-1 text-xs font-medium"
                  >
                    Details <ChevronRight className="h-3 w-3" />
                  </Link>
                </td>
              </tr>
            ))}
            {nodes.length === 0 && (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-slate-500">
                  No nodes registered yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
