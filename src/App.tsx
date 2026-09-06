import React, { useState, useEffect, useMemo } from 'react';
import { Header } from './components/Header';
import { HeroBanner } from './components/HeroBanner';
import { ArticleCard } from './components/ArticleCard';
import { TrendingSidebar } from './components/TrendingSidebar';
import { HubStatsSidebar } from './components/HubStatsSidebar';
import { ArticleModal } from './components/ArticleModal';
import { AdminModal } from './components/AdminModal';
import { Footer } from './components/Footer';
import { Article, RSSSource, HubStats, CategoryFilter } from './types';
import { INITIAL_ARTICLES, INITIAL_SOURCES, INITIAL_STATS } from './data/initialData';

export default function App() {
  const [articles, setArticles] = useState<Article[]>(INITIAL_ARTICLES);
  const [sources, setSources] = useState<RSSSource[]>(INITIAL_SOURCES);
  const [stats, setStats] = useState<HubStats>(INITIAL_STATS);

  const [activeTab, setActiveTab] = useState<CategoryFilter>('Latest');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isAdminOpen, setIsAdminOpen] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Auto-refresh countdown timer (seconds)
  const [countdown, setCountdown] = useState<number>(765); // ~12m 45s

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 1 ? prev - 1 : 1800));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCountdown = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  // Fetch live articles & stats from server API if available
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [artRes, srcRes, statsRes] = await Promise.all([
          fetch('/api/articles'),
          fetch('/api/sources'),
          fetch('/api/stats'),
        ]);

        if (artRes.ok) {
          const artData = await artRes.json();
          if (artData.items && artData.items.length > 0) {
            setArticles(artData.items);
          }
        }

        if (srcRes.ok) {
          const srcData = await srcRes.json();
          if (srcData.sources && srcData.sources.length > 0) {
            setSources(srcData.sources);
          }
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } catch (err) {
        console.warn('Using client-side fallback data:', err);
      }
    };

    loadInitialData();
  }, []);

  // Trigger manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch('/api/fetch-now', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setStats((prev) => ({
          ...prev,
          last_refresh: data.last_refresh,
          articles_today: data.articles_today || prev.articles_today + 1,
        }));
      }
    } catch (e) {
      console.warn('Refresh simulated on client');
    } finally {
      setTimeout(() => {
        setIsRefreshing(false);
        setCountdown(1800); // reset 30m
      }, 800);
    }
  };

  // Toggle source in admin
  const handleToggleSource = async (id: string) => {
    try {
      const res = await fetch(`/api/sources/${id}/toggle`, { method: 'PATCH' });
      if (res.ok) {
        const data = await res.json();
        setSources((prev) =>
          prev.map((s) => (s.id === id ? data.source : s))
        );
        setStats((prev) => ({
          ...prev,
          active_sources: sources.filter((s) => (s.id === id ? !s.enabled : s.enabled)).length,
        }));
        return;
      }
    } catch (e) {
      // client-side toggle fallback
    }

    setSources((prev) =>
      prev.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s))
    );
  };

  // Filter and sort articles
  const filteredArticles = useMemo(() => {
    let result = [...articles];

    // Category filter
    if (activeTab === 'Trending') {
      result.sort((a, b) => b.trending_score - a.trending_score);
    } else if (activeTab !== 'Latest' && activeTab !== 'All') {
      result = result.filter(
        (a) => a.category.toLowerCase() === activeTab.toLowerCase()
      );
    }

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (a) =>
          a.title.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          a.summary.toLowerCase().includes(q) ||
          a.source_name.toLowerCase().includes(q) ||
          a.tags.some((t) => t.toLowerCase().includes(q))
      );
    }

    return result;
  }, [articles, activeTab, searchQuery]);

  // Hero article is top hero or first item
  const heroArticle = useMemo(() => {
    return articles.find((a) => a.is_hero) || articles[0];
  }, [articles]);

  // Grid articles (excluding hero if on Latest)
  const gridArticles = useMemo(() => {
    if (activeTab === 'Latest' && !searchQuery) {
      return filteredArticles.filter((a) => a.id !== heroArticle.id);
    }
    return filteredArticles;
  }, [filteredArticles, heroArticle, activeTab, searchQuery]);

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* Header */}
      <Header
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          setSearchQuery('');
        }}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onOpenAdmin={() => setIsAdminOpen(true)}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden p-4 md:p-6 gap-6">
        {/* Left Column: News Feed */}
        <main className="flex-1 flex flex-col gap-6 overflow-y-auto pr-0 lg:pr-2">
          {/* Breaking News Hero Banner (shown when on Latest and no active search) */}
          {activeTab === 'Latest' && !searchQuery && heroArticle && (
            <HeroBanner
              article={heroArticle}
              onOpenArticle={(art) => setSelectedArticle(art)}
            />
          )}

          {/* Feed Header */}
          <div className="flex flex-col flex-1 min-h-0">
            <div className="flex items-center justify-between mb-3 shrink-0">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-bold text-slate-900">
                  {searchQuery
                    ? `Search Results for "${searchQuery}"`
                    : activeTab === 'Trending'
                    ? 'Trending AI Stories'
                    : activeTab === 'Latest'
                    ? 'Latest Technical Blogs'
                    : `${activeTab} Developments`}
                </h3>
                <span className="text-xs bg-slate-200/70 text-slate-700 font-semibold px-2 py-0.5 rounded-full">
                  {gridArticles.length} stories
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                Auto-refresh in {formatCountdown(countdown)}
              </div>
            </div>

            {/* Grid of Articles */}
            {gridArticles.length === 0 ? (
              <div className="bg-white border border-slate-200 rounded-xl p-12 text-center flex flex-col items-center justify-center">
                <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mb-3 text-lg font-bold">
                  ∅
                </div>
                <h4 className="text-sm font-bold text-slate-700 mb-1">No articles matched your criteria</h4>
                <p className="text-xs text-slate-500 max-w-sm mb-4">
                  Try adjusting your search query or switching to another category.
                </p>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setActiveTab('Latest');
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2 rounded-lg cursor-pointer"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pb-6">
                {gridArticles.map((article) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    onOpenArticle={(art) => setSelectedArticle(art)}
                  />
                ))}
              </div>
            )}
          </div>
        </main>

        {/* Right Aside: Trending & Hub Statistics */}
        <aside className="w-full lg:w-80 flex flex-col sm:flex-row lg:flex-col gap-6 shrink-0 overflow-y-auto">
          <TrendingSidebar
            articles={articles}
            onOpenArticle={(art) => setSelectedArticle(art)}
          />

          <HubStatsSidebar
            stats={stats}
            onRefresh={handleRefresh}
            isRefreshing={isRefreshing}
          />
        </aside>
      </div>

      {/* Footer */}
      <Footer uptime={stats.uptime} />

      {/* Deep Dive Article Modal */}
      <ArticleModal
        article={selectedArticle}
        onClose={() => setSelectedArticle(null)}
      />

      {/* Administration Portal Modal */}
      <AdminModal
        isOpen={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
        sources={sources}
        stats={stats}
        onToggleSource={handleToggleSource}
        onRefreshFeeds={handleRefresh}
      />
    </div>
  );
}
