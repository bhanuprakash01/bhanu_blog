import React from 'react';

interface FooterProps {
  uptime: string;
}

export const Footer: React.FC<FooterProps> = ({ uptime }) => {
  return (
    <footer className="bg-white border-t border-slate-200 px-6 py-2 flex items-center justify-between shrink-0 text-[10px] text-slate-400 uppercase font-bold select-none">
      <div>&copy; 2026 AI News Hub • Proxmox Home Server Instance</div>
      <div className="flex items-center gap-6">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full shadow-[0_0_6px_rgba(34,197,94,0.6)]"></span>
          <span>API: Connected</span>
        </span>
        <span>Uptime: {uptime}</span>
      </div>
    </footer>
  );
};
