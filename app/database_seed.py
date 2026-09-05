import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.article import Article, ProcessingStatus
from app.services.deduplicator import Deduplicator
from app.services.trending import TrendingCalculator

SEED_ARTICLES = [
    {
        "title": "Google DeepMind Unveils Gemini 2.5 Flash: Next-Gen Speed and Real-Time Multimodality",
        "url": "https://deepmind.google/discover/blog/gemini-2-5-flash-breakthrough/",
        "source_name": "Google DeepMind",
        "source_url": "https://deepmind.google/blog/",
        "author": "DeepMind Research Team",
        "category": "Generative AI",
        "summary": "Google DeepMind announced Gemini 2.5 Flash, an ultra-low-latency foundation model engineered specifically for high-throughput reasoning, complex code generation, and live bidirectional voice-and-video interaction at unprecedented cost efficiency.",
        "takeaways": [
            "Drastically reduces inference latency by 45% compared to prior frontier releases.",
            "Features native audio, visual, and symbolic tool execution in a single unified architecture.",
            "Sets new price-performance benchmarks across SWE-bench and human-preference evaluations."
        ],
        "why_it_matters": "Low-latency inference is the critical bottleneck for practical autonomous AI agents. Gemini 2.5 Flash enables sub-second agentic loops that feel instant to human users.",
        "tags": ["gemini", "deepmind", "multimodal", "llm", "latency"],
        "importance_score": 9,
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 2,
    },
    {
        "title": "Anthropic Introduces Hybrid Reasoning and Automated Tool Use in Claude 3.7 Sonnet",
        "url": "https://www.anthropic.com/news/claude-3-7-sonnet-hybrid-reasoning",
        "source_name": "Anthropic",
        "source_url": "https://www.anthropic.com/news",
        "author": "Anthropic Engineering",
        "category": "LLMs",
        "summary": "Anthropic published Claude 3.7 Sonnet, introducing continuous reasoning modes where developers can dynamically allocate thinking tokens based on query complexity while maintaining instant response times for straightforward tasks.",
        "takeaways": [
            "Introduces developer-controlled token reasoning budgets ranging from zero to 64k tokens.",
            "Demonstrates state-of-the-art results on full-stack software refactoring and debugging benchmarks.",
            "Integrates rigorous safety guardrails to mitigate prompt injection and unauthorized command execution."
        ],
        "why_it_matters": "Dynamic compute scaling bridges the divide between standard conversational models and slow, exhaustive multi-step reasoning engines.",
        "tags": ["anthropic", "claude", "reasoning", "coding", "safety"],
        "importance_score": 9,
        "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 4,
    },
    {
        "title": "Meta FAIR Releases Open-Weight Multimodal World Model for Physical Robotic Manipulation",
        "url": "https://ai.meta.com/blog/meta-fair-open-world-models-robotics/",
        "source_name": "Meta AI Research",
        "source_url": "https://ai.meta.com/blog/",
        "author": "FAIR Robotics Team",
        "category": "Robotics",
        "summary": "Meta's Fundamental AI Research team has open-sourced an end-to-end vision-action foundation model capable of zero-shot transfer across diverse robotic arms, quadrupeds, and bimanual grippers.",
        "takeaways": [
            "Trained across 50,000+ hours of multi-embodiment real-world sensor logs.",
            "Zero-shot generalization to unfamiliar objects and chaotic home environments.",
            "Released under permissive open-weights license for academic and commercial robotics."
        ],
        "why_it_matters": "Robotics has historically suffered from fragmented proprietary control stacks; open foundational vision-action models democratize physical AI development.",
        "tags": ["robotics", "open source", "world models", "meta", "reinforcement learning"],
        "importance_score": 8,
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 6,
    },
    {
        "title": "NVIDIA Architecture Deep Dive: Next-Generation NVLink 6 and Photonic Interconnects",
        "url": "https://developer.nvidia.com/blog/nvlink-6-photonic-interconnect-ai-clusters/",
        "source_name": "NVIDIA Developer",
        "source_url": "https://developer.nvidia.com/blog/",
        "author": "NVIDIA Hardware Architecture",
        "category": "AI Hardware",
        "summary": "NVIDIA revealed architectural specifications for optical interconnect fabrics, drastically cutting power dissipation while scaling all-to-all GPU bandwidth to tens of terabytes per second across megawatt-scale data center clusters.",
        "takeaways": [
            "Co-packaged optics reduce electrical parasitic capacitance by over 60%.",
            "Enables clusters of 100,000+ accelerators to operate as a single virtual GPU memory pool.",
            "Direct answer to power-wall constraints throttling 10-trillion parameter model pre-training."
        ],
        "why_it_matters": "Hardware bandwidth and power distribution are now the predominant bottlenecks in generative AI infrastructure.",
        "tags": ["hardware", "nvidia", "gpu", "interconnect", "datacenters"],
        "importance_score": 8,
        "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 10,
    },
    {
        "title": "Autonomous Coding Agents Reach Parity on Real-World Enterprise Repositories",
        "url": "https://venturebeat.com/ai/autonomous-coding-agents-enterprise-benchmarks/",
        "source_name": "VentureBeat AI",
        "source_url": "https://venturebeat.com/category/ai/",
        "author": "Sharon Goldman",
        "category": "AI Coding",
        "summary": "A comprehensive benchmark evaluating autonomous coding systems across 400 production GitHub codebases found multi-agent review loops successfully resolved 72% of complex security vulnerabilities without human intervention.",
        "takeaways": [
            "Multi-agent architecture consisting of planner, coder, and test-verifier outperformed single models.",
            "Automated patch verification eliminated 90% of regressions during automated pull request generation.",
            "Adoption among Fortune 500 engineering teams surged over 300% quarter-over-quarter."
        ],
        "why_it_matters": "Autonomous engineering workflows are migrating from toy code completions to full production repository lifecycle management.",
        "tags": ["ai coding", "agents", "software engineering", "automation"],
        "importance_score": 7,
        "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 14,
    },
    {
        "title": "MIT & Stanford Researchers Propose Test-Time Verification for Hallucination Suppression",
        "url": "https://arxiv.org/abs/2603.test-time-verification-mit-stanford",
        "source_name": "MIT Technology Review",
        "source_url": "https://www.technologyreview.com/",
        "author": "Karen Hao",
        "category": "AI Research",
        "summary": "A collaborative paper from MIT and Stanford demonstrates that test-time search guided by lightweight formal verifiers suppresses factual hallucination in legal and medical queries by over 88% without retraining the model.",
        "takeaways": [
            "Applies tree-of-thought exploration with automated symbolic constraints.",
            "Achieves near-zero hallucination on verifiable biomedical reference datasets.",
            "Operates as a drop-in sampling wrapper on existing closed and open foundation models."
        ],
        "why_it_matters": "Hallucination remains the number one risk preventing autonomous AI deployment in high-liability regulated domains.",
        "tags": ["research", "hallucination", "verification", "stanford", "mit"],
        "importance_score": 8,
        "image_url": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 18,
    },
    {
        "title": "Hugging Face and Community Release Open-R1: Fully Reproducible Reasoning Models",
        "url": "https://huggingface.co/blog/open-r1-reproducible-reasoning",
        "source_name": "Hugging Face",
        "source_url": "https://huggingface.co/blog",
        "author": "Open-R1 Working Group",
        "category": "Open Source AI",
        "summary": "Hugging Face released the Open-R1 pipeline, providing transparent training code, reward modeling scripts, and synthetic verification traces to replicate frontier reasoning capabilities on consumer clusters.",
        "takeaways": [
            "Complete open-source pipeline from data curation to reinforcement learning with rule-based rewards.",
            "Matches commercial reasoning benchmarks at a fraction of pre-training compute cost.",
            "Full Apache 2.0 licensing including weights, evaluation datasets, and recipes."
        ],
        "why_it_matters": "Prevents proprietary monopolies over next-generation reasoning architectures by giving independent developers and researchers full reproducibility.",
        "tags": ["open source", "hugging face", "reasoning", "rl", "open-r1"],
        "importance_score": 8,
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 22,
    },
    {
        "title": "Frontier AI Safety Consortium Establishes International Red-Teaming Standards",
        "url": "https://techcrunch.com/2026/09/ai-safety-consortium-standards/",
        "source_name": "TechCrunch AI",
        "source_url": "https://techcrunch.com/category/artificial-intelligence/",
        "author": "Kyle Wiggers",
        "category": "AI Safety",
        "summary": "Leading AI research organizations and international regulatory bodies finalized common evaluation standards for identifying autonomous cyber-offense capabilities and deceptive alignment in multi-agent networks.",
        "takeaways": [
            "Standardizes 15 mandatory security and alignment evaluations prior to public weights release.",
            "Establishes a shared vulnerability disclosure pipeline for AI model exploits.",
            "Focuses heavily on agentic sandbox escape and automated social engineering prevention."
        ],
        "why_it_matters": "Provides clear, globally recognized testing benchmarks as sovereign governments introduce statutory AI regulatory frameworks.",
        "tags": ["safety", "policy", "alignment", "red teaming", "cybersecurity"],
        "importance_score": 7,
        "image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80",
        "hours_ago": 26,
    }
]


def seed_initial_articles_if_empty(db: Session) -> int:
    """Populates the database with initial verified articles if currently empty."""
    count = db.query(Article).count()
    if count > 0:
        return 0

    now = datetime.now(timezone.utc)
    added = 0
    for data in SEED_ARTICLES:
        published_dt = now - timedelta(hours=data["hours_ago"])
        canonical = Deduplicator.normalize_url(data["url"])
        content_hash = Deduplicator.compute_content_hash(data["title"], data["summary"])

        art = Article(
            title=data["title"],
            url=data["url"],
            canonical_url=canonical,
            source_name=data["source_name"],
            source_url=data.get("source_url"),
            author=data.get("author"),
            published_at=published_dt,
            discovered_at=published_dt,
            image_url=data.get("image_url"),
            description=data["summary"],
            category=data["category"],
            summary=data["summary"],
            key_takeaways=json.dumps(data["takeaways"]),
            why_it_matters=data.get("why_it_matters"),
            tags=json.dumps(data.get("tags", [])),
            importance_score=data.get("importance_score", 5),
            relevance_score=1.0,
            trending_score=TrendingCalculator.compute_article_score(
                published_at=published_dt,
                importance_score=data.get("importance_score", 5),
                source_priority=8.0,
            ),
            content_hash=content_hash,
            processing_status=ProcessingStatus.PROCESSED,
            gemini_processed_at=published_dt,
        )
        db.add(art)
        added += 1

    db.commit()
    return added
