import React from 'react';
import { LayoutDashboard, Server, AlertTriangle, Network, Settings } from 'lucide-react';
import Logo from './Logo';

export default function Sidebar() {
  const menuItems = [
    { icon: <LayoutDashboard size={24} />, label: 'Dashboard', active: true },
    { icon: <Server size={24} />, label: 'Nodes', active: false },
    { icon: <AlertTriangle size={24} />, label: 'Alerts', active: false },
    { icon: <Network size={24} />, label: 'Network', active: false },
    { icon: <Settings size={24} />, label: 'Settings', active: false },
  ];

  return (
    <div className="h-screen w-20 bg-slate-950 border-r border-slate-800/50 flex flex-col items-center py-6 fixed left-0 top-0 z-50 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <div className="mb-10 hover:scale-110 transition-transform duration-300 drop-shadow-[0_0_10px_rgba(0,255,200,0.5)]">
        <Logo size="icon" />
      </div>
      
      <div className="flex flex-col gap-8 w-full">
        {menuItems.map((item, index) => (
          <button 
            key={index}
            className={`w-full flex justify-center py-3 relative transition-all duration-200 group ${
              item.active ? 'text-[rgb(0,255,200)]' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {item.active && (
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-[rgb(0,255,200)] rounded-r-full shadow-[0_0_15px_rgb(0,255,200)]" />
            )}
            <div className="relative">
               {item.icon}
               {!item.active && <div className="absolute inset-0 bg-[rgb(0,255,200)] opacity-0 group-hover:opacity-20 blur-lg transition-opacity rounded-full"></div>}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
