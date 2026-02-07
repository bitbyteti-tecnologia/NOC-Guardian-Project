import React from 'react';
import { LayoutDashboard, Server, AlertTriangle, Settings } from 'lucide-react';
import Logo from './Logo';

export default function Sidebar({ isOpen, closeSidebar }) {
  const menuItems = [
    { icon: <LayoutDashboard size={24} />, label: 'Dashboard', active: true },
    { icon: <Server size={24} />, label: 'Nodes', active: false },
    { icon: <AlertTriangle size={24} />, label: 'Alerts', active: false },
    { icon: <Settings size={24} />, label: 'Settings', active: false },
  ];

  return (
    <>
      {/* Mobile Overlay - Only visible when drawer is open on mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/80 z-30 lg:hidden backdrop-blur-sm transition-opacity"
          onClick={closeSidebar}
        />
      )}

      <aside className={`
        fixed top-16 left-0 z-40 h-[calc(100vh-4rem)] bg-[#020617] border-r border-slate-800/50 
        flex flex-col py-6 shadow-[0_0_20px_rgba(0,0,0,0.5)] overflow-hidden group
        transition-all duration-300 ease-in-out
        w-64 lg:w-20 lg:hover:w-64
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* We removed the Logo from here as it's now in the Header */}
        
        <div className="flex flex-col gap-4 w-full px-3 lg:px-2 lg:group-hover:px-4 mt-2">
          {menuItems.map((item, index) => (
            <button 
              key={index}
              className={`w-full flex items-center p-3 rounded-xl transition-all duration-200 whitespace-nowrap overflow-hidden ${
                item.active 
                  ? 'bg-[#0b1220] text-[#38bdf8] shadow-[0_0_15px_rgba(56,189,248,0.1)] border border-[rgba(59,130,246,0.15)]' 
                  : 'text-slate-500 hover:text-slate-200 hover:bg-slate-900/50'
              }`}
            >
              <div className="min-w-[24px] flex justify-center">
                 {item.icon}
              </div>
              <span className={`
                ml-4 font-medium tracking-wide transition-opacity duration-300
                lg:opacity-0 lg:group-hover:opacity-100 lg:w-0 lg:group-hover:w-auto
                opacity-100 w-auto
              `}>
                  {item.label}
              </span>
            </button>
          ))}
        </div>
      </aside>
    </>
  );
}
