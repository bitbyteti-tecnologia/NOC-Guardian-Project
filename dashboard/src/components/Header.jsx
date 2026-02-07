import React from 'react';
import { Clock, Bell, Menu } from 'lucide-react';
import Logo from './Logo';

export default function Header({ toggleSidebar, metrics, currentTime }) {
    return (
        <header className="fixed top-0 left-0 w-full h-16 z-50 bg-[#020617] border-b border-slate-800/50 flex justify-between items-center px-4 md:px-8 shadow-lg backdrop-blur-md bg-opacity-90">
            <div className="flex items-center gap-4">
                {/* Mobile Menu Toggle */}
                <button 
                    onClick={toggleSidebar}
                    className="p-2 text-slate-400 hover:text-white lg:hidden transition-colors"
                >
                    <Menu size={24} />
                </button>

                <div className="flex items-center gap-3">
                    <div className="scale-75 origin-left">
                         <Logo size="icon" />
                    </div>
                    <div className="hidden sm:block h-6 w-px bg-slate-800 mx-2"></div>
                    <div className="hidden sm:flex flex-col">
                         <span className="text-slate-200 font-bold tracking-wider text-sm">NOC GUARDIAN</span>
                         <span className="text-[#38bdf8] text-[10px] tracking-[0.2em] uppercase font-mono">Enterprise Monitoring</span>
                    </div>
                </div>
            </div>
            
            <div className="flex items-center gap-3 md:gap-6">
                <div className="hidden md:flex items-center gap-3 px-4 py-1.5 bg-[#10b981]/10 border border-[#10b981]/20 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                    <div className="relative">
                        <div className="w-2.5 h-2.5 bg-[#10b981] rounded-full animate-ping absolute opacity-75"></div>
                        <div className="w-2.5 h-2.5 bg-[#10b981] rounded-full relative shadow-[0_0_5px_rgba(16,185,129,0.8)]"></div>
                    </div>
                    <span className="text-[#10b981] text-xs font-bold tracking-wider uppercase">System Operational</span>
                </div>

                <div className="flex items-center gap-3 text-slate-300 font-mono text-sm bg-[#0b1220] px-3 py-2 md:px-4 rounded-lg border border-[rgba(59,130,246,0.15)]">
                    <Clock size={16} className="text-[#38bdf8]" />
                    <span>{currentTime.toLocaleTimeString()}</span>
                </div>
                
                <button className="relative p-2 text-slate-400 hover:text-white transition-colors">
                    <Bell size={20} />
                    {metrics.criticalCount > 0 && (
                        <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-[#ef4444] rounded-full animate-ping border border-[#020617]"></span>
                    )}
                </button>
                
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#38bdf8] to-blue-600 p-[1px] hidden sm:block">
                    <div className="w-full h-full rounded-full bg-[#0b1220] flex items-center justify-center">
                         <span className="font-bold text-white text-xs">OP</span>
                    </div>
                </div>
            </div>
        </header>
    );
}
