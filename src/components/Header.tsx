import React from 'react';
import { Search, Rss, ShieldCheck, RefreshCw, User } from 'lucide-react';
import { CategoryFilter } from '../types';

interface HeaderProps {
  activeTab: CategoryFilter;
  onSelectTab: (tab: CategoryFilter) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onOpenAdmin: () => void;
  onOpenAbout: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
  searchQuery,
  onSearchChange,
  onOpenAdmin,
  onOpenAbout,
  onRefresh,
  isRefreshing,
}) => {
  const navTabs: { label: string; filter: CategoryFilter }[] = [
    { label: 'Latest', filter: 'Latest' },
    { label: 'Trending', filter: 'Trending' },
    { label: 'GenAI', filter: 'Generative AI' },
    { label: 'LLMs', filter: 'LLMs' },
    { label: 'Research', filter: 'Research' },
    { label: 'Robotics', filter: 'Robotics' },
    { label: 'Hardware', filter: 'AI Hardware' },
  ];

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shrink-0 shadow-xs">
      <div className="flex items-center gap-8">
        {/* Brand */}
        <button
          onClick={() => onSelectTab('Latest')}
          className="flex items-center gap-2 cursor-pointer focus:outline-none"
        >
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center shadow-xs">
            <div className="w-4 h-4 border-2 border-white rotate-45"></div>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 uppercase select-none">
            AI News Hub
          </h1>
        </button>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-500">
          {navTabs.map((tab) => {
            const isActive = activeTab === tab.filter;
            return (
              <button
                key={tab.label}
                onClick={() => onSelectTab(tab.filter)}
                className={`transition-colors py-1 cursor-pointer focus:outline-none ${
                  isActive
                    ? 'text-blue-600 font-bold border-b-2 border-blue-600'
                    : 'hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search AI topics..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="bg-slate-100 border-none rounded-full pl-9 pr-4 py-1.5 text-sm w-44 sm:w-64 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-900 placeholder:text-slate-400 transition-all"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-3 top-2 text-xs text-slate-400 hover:text-slate-600 font-bold"
            >
              &times;
            </button>
          )}
        </div>

        {/* Quick Refresh */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Poll RSS feeds now"
          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-full transition-colors cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
        </button>

        {/* Public RSS Feed */}
        <a
          href="/rss.xml"
          target="_blank"
          rel="noreferrer"
          title="Public RSS 2.0 Feed"
          className="hidden sm:flex items-center gap-1 text-xs text-slate-500 hover:text-amber-600 py-1.5 px-2.5 hover:bg-amber-50 rounded transition-colors"
        >
          <Rss className="w-3.5 h-3.5" />
          <span className="font-semibold">RSS</span>
        </a>

        {/* About Creator */}
        <button
          onClick={onOpenAbout}
          title="About Bhanu (Creator of AI News Hub)"
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 hover:text-blue-600 py-1.5 px-2.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
        >
          <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center text-[10px] font-bold shadow-xs">
            B
          </div>
          <span className="hidden sm:inline">About</span>
        </button>

        {/* Admin Button */}
        <button
          onClick={onOpenAdmin}
          className="bg-slate-900 text-white text-xs font-bold px-4 py-2 rounded uppercase tracking-wider hover:bg-slate-800 transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Admin</span>
        </button>
      </div>
    </header>
  );
};
