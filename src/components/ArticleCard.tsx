import React from 'react';
import { Sparkles, ExternalLink } from 'lucide-react';
import { Article } from '../types';

interface ArticleCardProps {
  article: Article;
  onOpenArticle: (article: Article) => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article, onOpenArticle }) => {
  // Format relative time helper
  const getRelativeTime = (isoString: string) => {
    const diffMs = Date.now() - new Date(isoString).getTime();
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    if (hours < 1) {
      const mins = Math.max(1, Math.floor(diffMs / (1000 * 60)));
      return `${mins}m ago`;
    }
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div
      onClick={() => onOpenArticle(article)}
      className="bg-white border border-slate-200 rounded-lg p-4 flex flex-col justify-between shadow-xs hover:border-slate-300 hover:shadow-sm transition-all duration-200 cursor-pointer group"
    >
      <div>
        {/* Source & Time */}
        <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 uppercase mb-2">
          <span className="truncate max-w-[160px] text-slate-700">{article.source_name}</span>
          <span className="text-slate-400 shrink-0">• {getRelativeTime(article.published_at)}</span>
        </div>

        {/* Title */}
        <h4 className="font-bold text-slate-900 text-sm leading-snug mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
          {article.title}
        </h4>

        {/* Excerpt */}
        <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
          {article.summary || article.description}
        </p>
      </div>

      {/* Footer Details */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-blue-600 font-semibold">
            Importance: {article.importance_score.toFixed(1)}
          </span>
          <span className="text-[9px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-medium">
            {article.category}
          </span>
        </div>

        <div className="flex items-center gap-1 text-[10px] text-slate-400 group-hover:text-blue-600 transition-colors">
          <Sparkles className="w-3 h-3 text-blue-500" />
          <span className="font-medium">Summarized</span>
        </div>
      </div>
    </div>
  );
};
