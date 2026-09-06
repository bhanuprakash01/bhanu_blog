import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Article } from '../types';

interface HeroBannerProps {
  article: Article;
  onOpenArticle: (article: Article) => void;
}

export const HeroBanner: React.FC<HeroBannerProps> = ({ article, onOpenArticle }) => {
  return (
    <section className="shrink-0 bg-white border border-slate-200 rounded-xl overflow-hidden flex flex-col md:flex-row shadow-xs min-h-[18rem]">
      {/* Visual Section */}
      <div className="w-full md:w-2/5 bg-slate-800 relative min-h-48 md:min-h-full overflow-hidden">
        {article.image_url ? (
          <img
            src={article.image_url}
            alt={article.title}
            referrerPolicy="no-referrer"
            className="w-full h-full object-cover object-center transition-transform duration-700 hover:scale-105"
          />
        ) : (
          <div className="absolute inset-0 bg-linear-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
            <div className="text-slate-400 italic text-sm text-center px-4 flex flex-col items-center gap-2">
              <Sparkles className="w-6 h-6 text-blue-400 opacity-60" />
              <span>Featured Visual: Frontier Multimodal Architecture</span>
            </div>
          </div>
        )}
        <div className="absolute inset-0 bg-linear-to-t from-slate-950/70 via-transparent to-transparent pointer-events-none" />
        
        {/* Breaking News Badge */}
        <div className="absolute top-4 left-4 bg-blue-600 text-white text-[10px] font-bold px-2.5 py-1 rounded uppercase tracking-wider shadow-sm flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-white rounded-full animate-ping" />
          <span>Breaking News</span>
        </div>
      </div>

      {/* Content Section */}
      <div className="flex-1 p-5 md:p-6 flex flex-col justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 mb-2">
            <span className="font-bold text-slate-700 uppercase">{article.source_name}</span>
            <span>•</span>
            <span>22 minutes ago</span>
            <span>•</span>
            <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">{article.category}</span>
            <span>•</span>
            <span className="text-blue-600 font-semibold text-[11px]">Score {article.trending_score.toFixed(0)}</span>
          </div>

          <h2
            onClick={() => onOpenArticle(article)}
            className="text-xl md:text-2xl lg:text-3xl font-extrabold text-slate-900 leading-tight mb-3 cursor-pointer hover:text-blue-600 transition-colors"
          >
            {article.title}
          </h2>

          <p className="text-slate-600 leading-relaxed text-sm line-clamp-3">
            {article.summary || article.description}
          </p>
        </div>

        <div className="flex items-center justify-between border-t border-slate-100 pt-4 mt-4">
          <div className="flex flex-wrap gap-2">
            {article.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-[10px] bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-100 font-medium"
              >
                {tag}
              </span>
            ))}
          </div>

          <button
            onClick={() => onOpenArticle(article)}
            className="text-blue-600 font-bold text-sm flex items-center gap-1 hover:text-blue-800 transition-colors cursor-pointer group"
          >
            <span>Read Summary</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </div>
      </div>
    </section>
  );
};
