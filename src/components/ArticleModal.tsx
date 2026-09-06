import React from 'react';
import { X, ExternalLink, Sparkles, CheckCircle2, ShieldAlert, Tag, Calendar, User } from 'lucide-react';
import { Article } from '../types';

interface ArticleModalProps {
  article: Article | null;
  onClose: () => void;
}

export const ArticleModal: React.FC<ArticleModalProps> = ({ article, onClose }) => {
  if (!article) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-start justify-between gap-4 sticky top-0 bg-white/95 backdrop-blur-xs z-10">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-500 mb-1.5">
              <span className="font-bold text-blue-600 uppercase">{article.source_name}</span>
              <span>•</span>
              <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-medium">{article.category}</span>
              <span>•</span>
              <span>Score {article.trending_score.toFixed(0)}</span>
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900 leading-snug">
              {article.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors cursor-pointer shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6">
          {/* Executive Summary */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>Gemini Executive Summary</span>
            </div>
            <p className="text-slate-700 leading-relaxed text-sm bg-slate-50 p-4 rounded-xl border border-slate-200">
              {article.summary || article.description}
            </p>
          </div>

          {/* Key Bullet Takeaways */}
          {article.key_takeaways && article.key_takeaways.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                Key Technical Takeaways
              </h3>
              <ul className="space-y-2.5">
                {article.key_takeaways.map((takeaway, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                    <span>{takeaway}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Why It Matters Callout */}
          {article.why_it_matters && (
            <div className="bg-blue-50/80 border border-blue-200 rounded-xl p-4">
              <div className="text-xs font-bold text-blue-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-blue-600" />
                <span>Strategic Industry Impact</span>
              </div>
              <p className="text-xs text-blue-950 leading-relaxed font-medium">
                {article.why_it_matters}
              </p>
            </div>
          )}

          {/* Metadata & Tags */}
          <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex flex-wrap gap-1.5 items-center">
              <Tag className="w-3.5 h-3.5 text-slate-400 mr-0.5" />
              {article.tags.map((tag) => (
                <span key={tag} className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[11px] font-medium">
                  {tag}
                </span>
              ))}
            </div>

            <div className="flex items-center gap-4 text-slate-500">
              <span className="font-semibold text-blue-600">
                Importance: {article.importance_score.toFixed(1)}/10
              </span>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 px-6 bg-slate-50 border-t border-slate-100 rounded-b-2xl flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Verified RSS Source: <strong className="text-slate-700">{article.source_name}</strong>
          </span>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
            >
              Close
            </button>
            <a
              href={article.url}
              target="_blank"
              rel="noreferrer"
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <span>Read Original Article</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
