import React from 'react';
import { X, Linkedin, Sparkles, ExternalLink, Quote, Layers, Cpu, Globe, CheckCircle2 } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur-xs z-10">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-blue-600 rounded flex items-center justify-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 uppercase tracking-tight">
                About the Creator
              </h2>
              <p className="text-xs text-slate-500">AI News Hub • Architectural Vision</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {/* Creator Profile Presentation */}
          <div className="flex items-center gap-4 p-4 bg-slate-50 border border-slate-200/80 rounded-xl">
            <div className="relative shrink-0">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 via-indigo-600 to-slate-900 p-0.5 shadow-sm flex items-center justify-center">
                <div className="w-full h-full bg-white rounded-full flex items-center justify-center text-slate-900 font-bold text-2xl tracking-tight">
                  <span className="bg-gradient-to-br from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                    B
                  </span>
                </div>
              </div>
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 rounded-full border-2 border-white flex items-center justify-center">
                <Sparkles className="w-2.5 h-2.5 text-white" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 leading-tight">
                Bhanu
              </h3>
              <p className="text-xs font-semibold text-blue-600">
                AI Enthusiast
              </p>
              <p className="text-[11px] text-slate-500 mt-1">
                Curator & Builder of AI News Hub
              </p>
            </div>
          </div>

          {/* Tagline Callout */}
          <div className="p-3 bg-blue-50/70 border border-blue-100 rounded-xl relative">
            <Quote className="w-3.5 h-3.5 text-blue-300 absolute top-2.5 left-2.5" />
            <p className="text-xs text-blue-950 font-medium italic pl-4">
              &ldquo;Exploring the future of Artificial Intelligence, one story at a time.&rdquo;
            </p>
          </div>

          {/* Full Bio */}
          <div className="space-y-3 text-sm text-slate-700 leading-relaxed">
            <p>
              Hi, I&apos;m Bhanu, an AI enthusiast passionate about exploring the rapidly evolving world of Artificial Intelligence, Generative AI, AI agents, and emerging technologies.
            </p>
            <p>
              I created AI News Hub to make it easier to keep up with the latest developments in AI. The goal is to bring together important AI news and technical updates from trusted sources and turn them into concise, easy-to-understand summaries.
            </p>
          </div>

          {/* Core Areas of Interest */}
          <div className="pt-2 border-t border-slate-100">
            <div className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
              Focus Areas & Interests
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Generative AI & LLMs</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Autonomous AI Agents</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>AI System Architecture</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Emerging Tech & Robotics</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer with LinkedIn Button */}
        <div className="p-4 px-6 bg-slate-50 border-t border-slate-100 rounded-b-2xl flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
          >
            Close
          </button>
          <a
            href="https://www.linkedin.com/in/bhanu-prakash-57a3746/"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-[#0A66C2] hover:bg-[#084e96] text-white text-xs font-bold px-4 py-2.5 rounded-lg transition-colors flex items-center gap-2 shadow-xs cursor-pointer group"
          >
            <Linkedin className="w-4 h-4 fill-current" />
            <span>Connect with me on LinkedIn</span>
            <ExternalLink className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </a>
        </div>
      </div>
    </div>
  );
};
