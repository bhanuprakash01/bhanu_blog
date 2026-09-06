import React, { useState } from 'react';
import { X, ShieldCheck, ToggleLeft, ToggleRight, Sparkles, Send, Check, AlertCircle, Database, Server } from 'lucide-react';
import { RSSSource, HubStats } from '../types';

interface AdminModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: RSSSource[];
  stats: HubStats;
  onToggleSource: (id: string) => void;
  onRefreshFeeds: () => void;
}

export const AdminModal: React.FC<AdminModalProps> = ({
  isOpen,
  onClose,
  sources,
  stats,
  onToggleSource,
  onRefreshFeeds,
}) => {
  const [activeTab, setActiveTab] = useState<'sources' | 'gemini_test' | 'system'>('sources');
  const [testTitle, setTestTitle] = useState('Google releases DeepSeek-R1 evaluation report');
  const [testContent, setTestContent] = useState('Researchers evaluated multi-step mathematical reasoning capabilities and found strong benchmark parity with o1.');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summaryResult, setSummaryResult] = useState<any>(null);

  if (!isOpen) return null;

  const handleTestGemini = async () => {
    setIsSummarizing(true);
    setSummaryResult(null);
    try {
      const res = await fetch('/api/summarize-live', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: testTitle, content: testContent }),
      });
      const data = await res.json();
      setSummaryResult(data);
    } catch (e: any) {
      setSummaryResult({ error: e.message });
    } finally {
      setIsSummarizing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white z-10">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-slate-900 rounded flex items-center justify-center text-white">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 uppercase tracking-tight">
                Hub Administration & Observability
              </h2>
              <p className="text-xs text-slate-500">Proxmox VE • Docker Container Instance</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-slate-100 px-6 gap-6 text-xs font-semibold bg-slate-50">
          <button
            onClick={() => setActiveTab('sources')}
            className={`py-3 transition-colors border-b-2 cursor-pointer ${
              activeTab === 'sources'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            RSS Feed Sources ({sources.length})
          </button>
          <button
            onClick={() => setActiveTab('gemini_test')}
            className={`py-3 transition-colors border-b-2 cursor-pointer ${
              activeTab === 'gemini_test'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            Test Gemini 3.8 Flash Pipeline
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`py-3 transition-colors border-b-2 cursor-pointer ${
              activeTab === 'system'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            System & Deduplication Status
          </button>
        </div>

        {/* Tab 1: Sources */}
        {activeTab === 'sources' && (
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-500">
                Manage automated RSS polling feeds. Disabled sources are omitted from collection cycles.
              </span>
              <button
                onClick={onRefreshFeeds}
                className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-3 py-1.5 rounded transition-colors"
              >
                Trigger Ingestion Now
              </button>
            </div>

            <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
              {sources.map((s) => (
                <div key={s.id} className="p-3.5 flex items-center justify-between bg-white hover:bg-slate-50/70 transition-colors">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-900">{s.name}</span>
                      <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                        {s.category}
                      </span>
                      <span className="text-[10px] text-blue-600 font-medium">
                        Priority: {s.priority}/10
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5 truncate max-w-md">
                      {s.feed_url}
                    </div>
                  </div>

                  <button
                    onClick={() => onToggleSource(s.id)}
                    className="flex items-center gap-1 text-xs font-semibold cursor-pointer"
                  >
                    {s.enabled ? (
                      <span className="text-green-600 flex items-center gap-1">
                        <ToggleRight className="w-6 h-6" /> Enabled
                      </span>
                    ) : (
                      <span className="text-slate-400 flex items-center gap-1">
                        <ToggleLeft className="w-6 h-6" /> Disabled
                      </span>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: Gemini Live Test */}
        {activeTab === 'gemini_test' && (
          <div className="p-6 space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 leading-relaxed">
              <strong>Server-Side Gemini 3.8 Flash Engine:</strong> Test real-time structured summarization and key takeaway extraction with the official Google GenAI SDK.
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Article Title</label>
                <input
                  type="text"
                  value={testTitle}
                  onChange={(e) => setTestTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Article Body / Excerpt</label>
                <textarea
                  rows={3}
                  value={testContent}
                  onChange={(e) => setTestContent(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <button
                onClick={handleTestGemini}
                disabled={isSummarizing}
                className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isSummarizing ? 'Processing with Gemini...' : 'Synthesize Article'}</span>
              </button>
            </div>

            {summaryResult && (
              <div className="mt-4 p-4 bg-slate-900 text-slate-200 rounded-xl font-mono text-xs overflow-x-auto space-y-2">
                <div className="text-green-400 font-bold">✓ Response from {summaryResult.model || 'Gemini'}</div>
                <pre className="whitespace-pre-wrap">{JSON.stringify(summaryResult, null, 2)}</pre>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: System Status */}
        {activeTab === 'system' && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Deduplication Engine</div>
                <div className="text-sm font-bold text-slate-900">4-Tier Hybrid Pipeline</div>
                <p className="text-xs text-slate-600 mt-1">
                  1. Exact URL • 2. Param Stripping • 3. SHA-256 Hash • 4. Jaccard &gt;0.85 Similarity
                </p>
              </div>

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Host Environment</div>
                <div className="text-sm font-bold text-slate-900">Proxmox VE Container (Docker)</div>
                <p className="text-xs text-slate-600 mt-1">
                  Uptime: {stats.uptime} • Port 3000 Ingress Reverse Proxy
                </p>
              </div>
            </div>

            <div className="p-4 bg-slate-900 text-slate-300 rounded-xl text-xs space-y-2">
              <div className="text-white font-bold uppercase tracking-wider mb-2 flex items-center gap-2">
                <Server className="w-4 h-4 text-blue-400" />
                <span>Live Container Diagnostics</span>
              </div>
              <div>• Collector Interval: 30 minutes</div>
              <div>• Relevance Filter: Strict AI & Deep Learning terms (Adobe Illustrator / non-AI excluded)</div>
              <div>• Gemini Model: {stats.model_name}</div>
              <div>• Last Ingestion Run: {new Date(stats.last_refresh).toLocaleString()}</div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
