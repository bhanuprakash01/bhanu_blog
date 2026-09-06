import React from 'react';
import { Linkedin } from 'lucide-react';

interface FooterProps {
  uptime: string;
  onOpenAbout: () => void;
}

export const Footer: React.FC<FooterProps> = ({ uptime, onOpenAbout }) => {
  return (
    <footer className="bg-white border-t border-slate-200 px-6 py-2.5 flex flex-wrap items-center justify-between gap-3 shrink-0 text-[11px] text-slate-500 font-medium select-none">
      <div className="flex items-center gap-3">
        <span>&copy; 2026 AI News Hub</span>
        <span className="text-slate-300">•</span>
        <div className="flex items-center gap-1.5">
          <span>Created by</span>
          <button
            onClick={onOpenAbout}
            className="font-bold text-slate-800 hover:text-blue-600 transition-colors cursor-pointer"
          >
            Bhanu
          </button>
          <span className="text-blue-600 text-[10px] font-semibold bg-blue-50 px-1.5 py-0.5 rounded">
            AI Enthusiast
          </span>
          <a
            href="https://www.linkedin.com/in/bhanu-prakash-57a3746/"
            target="_blank"
            rel="noopener noreferrer"
            title="Connect with Bhanu on LinkedIn"
            className="text-[#0A66C2] hover:text-[#084e96] ml-0.5 inline-flex items-center"
          >
            <Linkedin className="w-3.5 h-3.5 fill-current" />
          </a>
        </div>
      </div>

      <div className="flex items-center gap-5 text-[10px] uppercase font-bold text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full shadow-[0_0_6px_rgba(34,197,94,0.6)]"></span>
          <span>API: Connected</span>
        </span>
        <span>Proxmox Host • Uptime: {uptime}</span>
      </div>
    </footer>
  );
};
