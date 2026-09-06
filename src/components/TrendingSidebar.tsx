import React from 'react';
import { Article } from '../types';

interface TrendingSidebarProps {
  articles: Article[];
  onOpenArticle: (article: Article) => void;
}

export const TrendingSidebar: React.FC<TrendingSidebarProps> = ({ articles, onOpenArticle }) => {
  // Sort by trending score
  const trendingArticles = [...articles]
    .sort((a, b) => b.trending_score - a.trending_score)
    .slice(0, 4);

  return (
    <section className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs shrink-0">
      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest border-b border-slate-100 pb-3 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        <span>Trending Now</span>
      </h3>
      <ul className="space-y-4">
        {trendingArticles.map((item) => (
          <li
            key={item.id}
            onClick={() => onOpenArticle(item)}
            className="flex flex-col cursor-pointer group"
          >
            <span className="text-xs font-bold text-slate-800 group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug">
              {item.title}
            </span>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="text-[9px] bg-slate-100 px-1.5 py-0.5 rounded uppercase font-bold text-slate-600">
                Score {item.trending_score.toFixed(0)}
              </span>
              <span className="text-[9px] text-slate-400 italic">
                {item.related_stories_count || 12} Related Stories
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};
