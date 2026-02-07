import React from 'react';
import { Activity, Server, AlertTriangle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Header = () => (
  <header className="bg-slate-900 border-b border-slate-800 p-4">
    <div className="container mx-auto flex justify-between items-center">
      <Link to="/" className="flex items-center gap-2 text-xl font-bold text-blue-400">
        <Activity className="h-6 w-6" />
        NOC Guardian
      </Link>
      <div className="text-sm text-slate-400 flex items-center gap-4">
        <span className="flex items-center gap-1">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          System Operational
        </span>
        <span>{new Date().toLocaleTimeString()}</span>
      </div>
    </div>
  </header>
);

export const StatCard = ({ title, value, type = 'info', icon: Icon }) => {
  const colors = {
    info: 'bg-slate-800 border-slate-700 text-slate-100',
    success: 'bg-emerald-900/30 border-emerald-800 text-emerald-100',
    warning: 'bg-amber-900/30 border-amber-800 text-amber-100',
    danger: 'bg-rose-900/30 border-rose-800 text-rose-100',
  };

  return (
    <div className={`p-4 rounded-lg border ${colors[type]} flex items-center justify-between`}>
      <div>
        <h3 className="text-sm font-medium opacity-70 uppercase tracking-wider">{title}</h3>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      {Icon && <Icon className="h-8 w-8 opacity-50" />}
    </div>
  );
};

export const StatusBadge = ({ status }) => {
  const styles = {
    ONLINE: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    DEGRADED: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    OFFLINE: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    UNKNOWN: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold border ${styles[status] || styles.UNKNOWN}`}>
      {status}
    </span>
  );
};
