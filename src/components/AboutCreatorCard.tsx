import React from 'react';
import { Linkedin, Sparkles, ExternalLink, Quote } from 'lucide-react';

interface AboutCreatorCardProps {
  onOpenDetails?: () => void;
}

export const AboutCreatorCard: React.FC<AboutCreatorCardProps> = ({ onOpenDetails }) => {
  return (
    <section className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col text-slate-900 transition-all hover:border-slate-300">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-2.5">
        <h3 className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          About the Creator
        </h3>
        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
          <Sparkles className="w-2.5 h-2.5 text-blue-600" />
          Founder & Curator
        </span>
      </div>

      {/* Creator Profile Header */}
      <div className="flex flex-col items-center text-center">
        {/* Professional Avatar with AI accent aura */}
        <div className="relative mb-3 group">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 via-indigo-600 to-slate-900 p-0.5 shadow-md flex items-center justify-center">
            <div className="w-full h-full bg-white rounded-full flex items-center justify-center text-slate-900 font-bold text-2xl tracking-tight select-none">
              <span className="bg-gradient-to-br from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                B
              </span>
            </div>
          </div>
          {/* Active creator spark badge */}
          <div
            className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 rounded-full border-2 border-white flex items-center justify-center shadow-xs"
            title="AI News Hub Creator"
          >
            <Sparkles className="w-2.5 h-2.5 text-white" />
          </div>
        </div>

        {/* Creator Name & Title */}
        <h4 className="text-base font-bold text-slate-900 leading-snug">
          Bhanu
        </h4>
        <p className="text-xs font-semibold text-blue-600 mt-0.5">
          AI Enthusiast
        </p>

        {/* Quote / Tagline */}
        <div className="mt-3 px-2 py-2 bg-slate-50 border border-slate-100 rounded-lg w-full text-center relative">
          <Quote className="w-3 h-3 text-slate-300 absolute top-1.5 left-2" />
          <p className="text-[11px] text-slate-600 italic font-medium leading-relaxed px-3">
            &ldquo;Exploring the future of Artificial Intelligence, one story at a time.&rdquo;
          </p>
        </div>

        {/* Introduction */}
        <div className="mt-3 text-left space-y-2 text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-3">
          <p>
            Hi, I&apos;m Bhanu, an AI enthusiast passionate about exploring the rapidly evolving world of Artificial Intelligence, Generative AI, AI agents, and emerging technologies.
          </p>
          <p>
            I created AI News Hub to make it easier to keep up with the latest developments in AI. The goal is to bring together important AI news and technical updates from trusted sources and turn them into concise, easy-to-understand summaries.
          </p>
        </div>

        {/* Action Button */}
        <div className="mt-4 w-full pt-1">
          <a
            href="https://www.linkedin.com/in/bhanu-prakash-57a3746/"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full bg-[#0A66C2] hover:bg-[#084e96] text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-xs cursor-pointer group"
          >
            <Linkedin className="w-4 h-4 fill-current shrink-0" />
            <span>Connect with me on LinkedIn</span>
            <ExternalLink className="w-3 h-3 text-blue-200 group-hover:translate-x-0.5 transition-transform shrink-0" />
          </a>
        </div>
      </div>
    </section>
  );
};
