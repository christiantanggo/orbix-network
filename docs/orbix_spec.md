# Orbix Network Specification

## System Overview

Orbix Network is a fully automated media system that:
- Scrapes public news sources continuously
- Filters and scores stories using AI
- Generates short scripts
- Allows optional human review
- Automatically renders faceless studio-style videos
- Publishes videos to YouTube Shorts
- Tracks performance metrics

## Infrastructure

- **Supabase**: PostgreSQL, Auth, Storage
- **Railway**: Long-running Python workers, FFmpeg rendering, schedulers
- **Vercel**: Admin UI (Next.js)

## Content Categories

1. AI & Automation Takeovers
2. Corporate Collapses & Reversals
3. Tech Decisions With Massive Fallout
4. Laws & Rules That Quietly Changed Everything
5. Money & Market Shock

## Video Style

- Vertical 1080×1920
- 30–45 seconds
- Studio aesthetic (no visible host)
- 12 backgrounds: 6 stills + 6 motion loops
- Random selection at render time
- Calm, authoritative AI voiceover

## Pipeline Stages

1. Scraping → raw_items
2. AI Classification → stories
3. Shock Scoring → stories (threshold: 65)
4. Script Generation → scripts
5. Review Queue (optional) → review_queue
6. Rendering → renders
7. Publishing → publishes
8. Analytics → analytics_daily

