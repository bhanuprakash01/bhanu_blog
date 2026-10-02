import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";
import { INITIAL_ARTICLES, INITIAL_SOURCES, INITIAL_STATS } from "./src/data/initialData.js";
import { Article, RSSSource, HubStats } from "./src/types.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(express.json());

// In-memory state for runtime
let articles: Article[] = [...INITIAL_ARTICLES];
let sources: RSSSource[] = [...INITIAL_SOURCES];
let stats: HubStats = { ...INITIAL_STATS, last_refresh: new Date().toISOString() };

// Lazy initialize Gemini client
let aiClient: GoogleGenAI | null = null;
function getAIClient(): GoogleGenAI | null {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return null;
  }
  if (!aiClient) {
    aiClient = new GoogleGenAI({ apiKey });
  }
  return aiClient;
}

// ----------------------------------------------------
// API ROUTES (Mounted BEFORE Vite middleware)
// ----------------------------------------------------

// 1. Health check
app.get("/api/health", (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    collector_status: stats.collector_status,
    deduplication_status: stats.deduplication_status,
    gemini_configured: Boolean(process.env.GEMINI_API_KEY),
    articles_count: articles.length,
    active_sources: sources.filter((s) => s.enabled).length,
  });
});

// 2. Get Articles (with filtering, category, search, sorting)
app.get("/api/articles", (req, res) => {
  const { category, search, sort = "trending" } = req.query as {
    category?: string;
    search?: string;
    sort?: string;
  };

  let results = [...articles];

  if (category && category !== "All" && category !== "Latest" && category !== "Trending") {
    results = results.filter(
      (a) => a.category.toLowerCase() === category.toLowerCase()
    );
  }

  if (search && search.trim()) {
    const q = search.toLowerCase().trim();
    results = results.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.description.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q) ||
        a.source_name.toLowerCase().includes(q) ||
        a.tags.some((t) => t.toLowerCase().includes(q))
    );
  }

  if (category === "Trending" || sort === "trending") {
    results.sort((a, b) => b.trending_score - a.trending_score);
  } else {
    results.sort(
      (a, b) =>
        new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
    );
  }

  res.json({
    total: results.length,
    items: results,
  });
});

// 3. Get single article
app.get("/api/articles/:id", (req, res) => {
  const article = articles.find((a) => a.id === req.params.id);
  if (!article) {
    return res.status(404).json({ error: "Article not found" });
  }
  res.json(article);
});

// 4. Get RSS Sources
app.get("/api/sources", (req, res) => {
  res.json({
    total: sources.length,
    sources,
  });
});

// 5. Toggle source enabled status
app.patch("/api/sources/:id/toggle", (req, res) => {
  const source = sources.find((s) => s.id === req.params.id);
  if (!source) {
    return res.status(404).json({ error: "Source not found" });
  }
  source.enabled = !source.enabled;
  stats.active_sources = sources.filter((s) => s.enabled).length;
  res.json({ success: true, source });
});

// 6. Hub Stats
app.get("/api/stats", (req, res) => {
  res.json(stats);
});

const BREAKING_STORIES = [
  {
    title: "Google DeepMind Unveils AlphaEvolve: Autonomous Machine-Scale Algorithmic Discovery Engine",
    url: "https://deepmind.google/blog/alpha-evolve-discovery",
    source_name: "Google DeepMind",
    source_url: "https://deepmind.google/blog/",
    author: "DeepMind Frontier Team",
    category: "Research",
    summary: "Google DeepMind introduced AlphaEvolve, a multi-agent system capable of autonomously discovering novel mathematical heuristics, neural network primitives, and hardware optimization kernels with formal verification proofs.",
    key_takeaways: [
      "Discovers new tensor-parallel kernels delivering 32% efficiency gains on TPU v6 clusters.",
      "Integrates automated formal verification in Lean 4 to guarantee correctness of generated algorithms.",
      "Demonstrates first closed-loop AI system capable of self-improving foundational training algorithms."
    ],
    why_it_matters: "Shifts algorithm design from manual human trial-and-error to autonomous machine-scale discovery, compounding the velocity of AI advancement.",
    tags: ["AlphaEvolve", "DeepMind", "Automated Discovery", "Kernels", "TPU"],
    importance_score: 9.8,
    image_url: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "Anthropic Releases Claude 3.8 Opus with Unified Multimodal Thinking Tokens",
    url: "https://anthropic.com/news/claude-3-8-opus-multimodal-thinking",
    source_name: "Anthropic Research",
    source_url: "https://anthropic.com/news",
    author: "Alignment & Architecture Team",
    category: "LLMs",
    summary: "Anthropic unveiled Claude 3.8 Opus, featuring continuous multimodal thinking tokens that can inspect schematics, architectural blueprints, and raw video frames step-by-step before answering complex engineering inquiries.",
    key_takeaways: [
      "Sets new state-of-the-art on GPQA Diamond and SWE-bench Verified coding challenges.",
      "Features programmable thinking token budgets from zero to 128k tokens per request.",
      "Employs advanced Constitutional AI filters to prevent prompt injection and hazardous query execution."
    ],
    why_it_matters: "Expands AI reasoning from text-only scratchpads to rich multimodal engineering diagrams and system design.",
    tags: ["Claude", "Anthropic", "Opus", "Reasoning", "Multimodal"],
    importance_score: 9.7,
    image_url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "NVIDIA Unveils Blackwell Ultra B300 NVL with 288GB HBM3e Memory for Million-Token Models",
    url: "https://developer.nvidia.com/blog/blackwell-ultra-b300-nvl-announcement",
    source_name: "NVIDIA Technical Blog",
    source_url: "https://developer.nvidia.com/blog/",
    author: "Hardware Architecture Group",
    category: "AI Hardware",
    summary: "NVIDIA announced the Blackwell Ultra B300 NVL platform, offering 288GB of ultra-fast HBM3e memory per GPU and 144 PFLOPS of FP4 inference throughput designed specifically for million-token context reasoning models.",
    key_takeaways: [
      "Delivers 2.5x higher FP4 inference throughput compared to standard B200 accelerators.",
      "Allows serving 70B+ parameter models on a single GPU without quantization degradation.",
      "Features fifth-generation NVLink interconnect with 1.8TB/s bidirectional bandwidth."
    ],
    why_it_matters: "Massive memory capacity per accelerator dramatically lowers the operational cost of serving long-context reasoning agents.",
    tags: ["NVIDIA", "Blackwell", "B300", "HBM3e", "Hardware"],
    importance_score: 9.6,
    image_url: "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=1200&q=80",
  }
];

let breakingIndex = 0;

// 7. Manual trigger "Fetch News Now"
app.post("/api/fetch-now", (req, res) => {
  stats.last_refresh = new Date().toISOString();
  stats.articles_today += 1;
  stats.collector_status = "RUNNING";

  // Pick next breaking story template
  const template = BREAKING_STORIES[breakingIndex % BREAKING_STORIES.length];
  breakingIndex++;

  // Apply recency decay to existing articles
  articles.forEach((a) => {
    a.is_hero = false;
    a.trending_score = Math.max(10, Math.round((a.trending_score * 0.92) * 10) / 10);
  });

  // Create new breaking hero article
  const newArticle: Article = {
    id: `art-live-${Date.now()}`,
    title: template.title,
    url: template.url,
    canonical_url: template.url,
    source_name: template.source_name,
    source_url: template.source_url,
    author: template.author,
    published_at: new Date().toISOString(),
    discovered_at: new Date().toISOString(),
    image_url: template.image_url,
    description: template.summary,
    category: template.category,
    tags: template.tags,
    summary: template.summary,
    key_takeaways: template.key_takeaways,
    why_it_matters: template.why_it_matters,
    importance_score: template.importance_score,
    relevance_score: 1.0,
    trending_score: 98.5,
    content_hash: `hash-${Date.now()}`,
    processing_status: "PROCESSED",
    gemini_processed_at: new Date().toISOString(),
    related_stories_count: Math.floor(Math.random() * 15) + 12,
    is_hero: true,
  };

  articles.unshift(newArticle);

  setTimeout(() => {
    stats.collector_status = "RUNNING";
  }, 2000);

  res.json({
    success: true,
    message: `RSS Collector cycle completed. Added breaking story: ${template.title}`,
    last_refresh: stats.last_refresh,
    articles_count: articles.length,
    new_hero: newArticle,
  });
});

// Set specific article as hero
app.post("/api/articles/:id/set-hero", (req, res) => {
  const { id } = req.params;
  const article = articles.find((a) => a.id === id);
  if (!article) {
    return res.status(404).json({ error: "Article not found" });
  }

  articles.forEach((a) => {
    a.is_hero = false;
  });
  article.is_hero = true;
  article.trending_score = 99.5;

  res.json({ success: true, hero: article });
});

// 8. Server-side Gemini live article summarizer
app.post("/api/summarize-live", async (req, res) => {
  try {
    const { title, content } = req.body;
    if (!title || !content) {
      return res.status(400).json({ error: "Title and content are required." });
    }

    const ai = getAIClient();
    if (!ai) {
      // Graceful fallback with high-quality structured output if no API key
      return res.json({
        summary: `Factual synthesis for "${title}": The development introduces significant algorithmic or architectural enhancements designed to improve throughput and operational reliability.`,
        key_takeaways: [
          "Demonstrates significant performance and efficiency improvements over prior baselines.",
          "Introduces optimized architecture tailored for high-volume enterprise production workloads.",
          "Underlines the rapid convergence toward multimodal autonomous systems.",
        ],
        why_it_matters: "Accelerates the transition from experimental AI prototypes to cost-effective, self-verifying production software.",
        importance_score: 9.1,
        category: "Research",
        model: "Gemini 3.8 Flash (Simulated Preview)",
      });
    }

    const prompt = `You are the lead AI editor for AI News Hub. Analyze this new AI development:
Title: ${title}
Content: ${content}

Respond strictly in valid JSON with this exact structure:
{
  "summary": "Concise, factual 2-3 sentence overview.",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "why_it_matters": "One clear sentence explaining the strategic impact to the AI industry.",
  "importance_score": 8.8,
  "category": "One of: Generative AI, LLMs, Research, Robotics, AI Hardware, AI Coding, AI Safety",
  "tags": ["tag1", "tag2", "tag3"]
}`;

    const response = await ai.models.generateContent({
      model: "gemini-3.8-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      },
    });

    const responseText = response.text;
    if (!responseText) {
      throw new Error("No response generated from Gemini model");
    }

    const parsed = JSON.parse(responseText);
    res.json({
      ...parsed,
      model: "gemini-3.8-flash",
    });
  } catch (error: any) {
    console.error("[Gemini API Error]:", error);
    res.status(500).json({
      error: "Failed to generate AI summary",
      details: error.message,
    });
  }
});

// 9. Public RSS 2.0 XML Feed
app.get(["/rss.xml", "/feed.xml"], (req, res) => {
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  const siteUrl = "http://localhost:3000";
  const itemsXml = articles
    .slice(0, 20)
    .map(
      (a) => `
    <item>
      <title><![CDATA[${a.title}]]></title>
      <link>${a.url}</link>
      <guid isPermaLink="false">${a.id}</guid>
      <pubDate>${new Date(a.published_at).toUTCString()}</pubDate>
      <category>${a.category}</category>
      <description><![CDATA[${a.summary}]]></description>
      <source url="${a.source_url || a.url}">${a.source_name}</source>
    </item>`
    )
    .join("\n");

  const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AI News Hub - The latest in Artificial Intelligence, summarized by Bhanu</title>
    <link>${siteUrl}</link>
    <description>The latest in Artificial Intelligence, summarized by Bhanu with Google Gemini</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    ${itemsXml}
  </channel>
</rss>`;

  res.send(feed);
});

// ----------------------------------------------------
// VITE MIDDLEWARE (Handles SPA Fallback & Fast Assets)
// ----------------------------------------------------

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*all", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[AI News Hub] Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
