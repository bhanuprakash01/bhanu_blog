import React from 'react';
import { RefreshCw, Play } from 'lucide-react';
import { HubStats } from '../types';

interface HubStatsSidebarProps {
  stats: HubStats;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const HubStatsSidebar: React.FC<HubStatsSidebarProps> = ({
  stats,
  onRefresh,
  isRefreshing,
}) => {
  const percentage = Math.round((stats.active_sources / stats.total_sources) * 100);

  return (
    <section className="bg-slate-900 text-slate-300 rounded-xl p-5 shadow-lg flex flex-col justify-between flex-1">
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white text-sm font-bold uppercase tracking-wider">
            Hub Statistics
          </h3>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 cursor-pointer transition-colors"
          >
            <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
            <span>Poll</span>
          </button>
        </div>

        <div className="space-y-4">
          {/* Active Sources Progress */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Active Sources</span>
              <span className="text-white font-medium">
                {stats.active_sources}/{stats.total_sources}
              </span>
            </div>
            <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-blue-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
          </div>

          {/* 2x2 Stats Grid */}
          <div className="grid grid-cols-2 gap-3 py-1">
            <div className="bg-slate-800/90 p-3 rounded-lg border border-slate-700">
              <div className="text-[10px] uppercase font-bold text-slate-500">Today</div>
              <div className="text-lg font-bold text-white">{stats.articles_today}</div>
              <div className="text-[9px] text-green-400 font-medium">{stats.articles_growth}</div>
            </div>

            <div className="bg-slate-800/90 p-3 rounded-lg border border-slate-700">
              <div className="text-[10px] uppercase font-bold text-slate-500">Summary</div>
              <div className="text-lg font-bold text-white">{stats.summary_percentage}%</div>
              <div className="text-[9px] text-blue-400 font-medium truncate">{stats.model_name}</div>
            </div>
          </div>

          {/* Health Status */}
          <div className="mt-3 pt-2 border-t border-slate-800">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">
              Health Status
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-200">
              <span className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)] shrink-0"></span>
              <span>Collector Service Running</span>
            </div>

            <div className="flex items-center gap-2 text-xs mt-2 text-slate-300">
              <span className="w-2 h-2 bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.4)] shrink-0"></span>
              <span>4-Tier Deduplication Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trigger Quick Action */}
      <div className="mt-4 pt-3 border-t border-slate-800">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-2 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-sm disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isRefreshing ? 'Polling RSS Feeds...' : 'Fetch Feeds Now'}</span>
        </button>
      </div>
    </section>
  );
};
