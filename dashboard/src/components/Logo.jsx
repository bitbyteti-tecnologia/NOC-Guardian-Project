import React from 'react';

export default function Logo({ size = "full" }) {
  if (size === "icon") {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" className="w-8 h-8 drop-shadow-lg">
        <defs>
          <linearGradient id="gradIcon" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0ea5e9" />
            <stop offset="100%" stopColor="#22c55e" />
          </linearGradient>
        </defs>
        <path d="M50 5 L90 25 L90 75 L50 95 L10 75 L10 25 Z" fill="none" stroke="url(#gradIcon)" strokeWidth="5" />
        <circle cx="50" cy="50" r="15" fill="#0ea5e9" opacity="0.8" />
        <path d="M50 35 L50 65 M35 50 L65 50" stroke="#fff" strokeWidth="3" />
      </svg>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" className="h-12 w-auto drop-shadow-2xl">
        <defs>
          <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#1e293b" />
          </linearGradient>
          <linearGradient id="neonGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="50%" stopColor="#0ea5e9" />
            <stop offset="100%" stopColor="#eab308" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Shield Base */}
        <path 
          d="M60 10 C30 15, 10 30, 10 50 L10 70 C10 90, 30 105, 60 115 C90 105, 110 90, 110 70 L110 50 C110 30, 90 15, 60 10 Z" 
          fill="url(#shieldGrad)" 
          stroke="#334155" 
          strokeWidth="2" 
        />
        
        {/* Neon Border/Pulse */}
        <path 
          d="M60 15 C35 20, 15 32, 15 50 L15 70 C15 85, 30 100, 60 110 C90 100, 105 85, 105 70 L105 50 C105 32, 85 20, 60 15 Z" 
          fill="none" 
          stroke="url(#neonGrad)" 
          strokeWidth="2"
          filter="url(#glow)"
        />

        {/* Network Cluster Center */}
        <g transform="translate(60, 60)">
          <circle cx="0" cy="0" r="12" fill="#0ea5e9" opacity="0.3" />
          <circle cx="0" cy="0" r="6" fill="#fff" />
          
          <circle cx="-20" cy="-15" r="4" fill="#22c55e" />
          <line x1="-20" y1="-15" x2="0" y2="0" stroke="#22c55e" strokeWidth="1" />
          
          <circle cx="20" cy="-15" r="4" fill="#eab308" />
          <line x1="20" y1="-15" x2="0" y2="0" stroke="#eab308" strokeWidth="1" />
          
          <circle cx="0" cy="25" r="4" fill="#0ea5e9" />
          <line x1="0" y1="25" x2="0" y2="0" stroke="#0ea5e9" strokeWidth="1" />
        </g>

        {/* Magnifying Glass (Monitoring) */}
        <g transform="translate(70, 70) rotate(-45)">
           <circle cx="0" cy="0" r="10" fill="none" stroke="#fff" strokeWidth="2" opacity="0.6" />
           <line x1="0" y1="10" x2="0" y2="20" stroke="#fff" strokeWidth="2" opacity="0.6" />
        </g>

        {/* Tech Elements (Simplified) */}
        {/* Python-ish curve left */}
        <path d="M30 80 Q20 90 30 100" fill="none" stroke="#3b82f6" strokeWidth="2" opacity="0.5" />
        {/* React-ish orbit right */}
        <ellipse cx="90" cy="80" rx="8" ry="3" stroke="#0ea5e9" strokeWidth="1" fill="none" transform="rotate(45 90 80)" opacity="0.5" />
        
        {/* Heartbeat Line */}
        <polyline points="25 60 35 60 40 50 45 70 50 60 95 60" fill="none" stroke="#22c55e" strokeWidth="1" opacity="0.4" />
        
      </svg>
      <div className="flex flex-col">
        <span className="text-2xl font-bold text-white tracking-widest font-mono uppercase">
          NOC <span className="text-blue-400">Guardian</span>
        </span>
        <span className="text-[0.6rem] text-slate-400 tracking-[0.2em] uppercase border-t border-slate-700 mt-1 pt-1">
          Enterprise Monitoring
        </span>
      </div>
    </div>
  );
}
