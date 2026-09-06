export interface Article {
  id: string;
  title: string;
  url: string;
  canonical_url: string;
  source_name: string;
  source_url?: string;
  author?: string;
  published_at: string;
  discovered_at: string;
  image_url?: string;
  description: string;
  category: string;
  summary: string;
  key_takeaways: string[];
  why_it_matters?: string;
  tags: string[];
  importance_score: number;
  relevance_score: number;
  trending_score: number;
  processing_status: 'PROCESSED' | 'PENDING' | 'FILTERED_OUT' | 'FAILED';
  gemini_processed_at?: string;
  related_stories_count?: number;
  is_hero?: boolean;
}

export interface RSSSource {
  id: string;
  name: string;
  feed_url: string;
  site_url: string;
  category: string;
  priority: number;
  enabled: boolean;
  last_polled_at?: string;
  article_count: number;
}

export interface HubStats {
  active_sources: number;
  total_sources: number;
  articles_today: number;
  articles_growth: string;
  summary_percentage: number;
  model_name: string;
  collector_status: 'RUNNING' | 'IDLE' | 'ERROR';
  deduplication_status: 'ACTIVE' | 'IDLE';
  uptime: string;
  last_refresh: string;
}

export type CategoryFilter = 'All' | 'Latest' | 'Trending' | 'Generative AI' | 'LLMs' | 'Research' | 'Robotics' | 'AI Hardware' | 'AI Coding' | 'AI Safety';
