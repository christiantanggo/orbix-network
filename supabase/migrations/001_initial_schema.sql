-- Orbix Network Database Schema

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('RSS', 'HTML')),
    enabled BOOLEAN DEFAULT true,
    fetch_interval_minutes INTEGER DEFAULT 60,
    category_hint TEXT,
    last_fetched_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Raw items table
CREATE TABLE IF NOT EXISTS raw_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    snippet TEXT,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'DISCARDED', 'PROCESSED')),
    discard_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_raw_items_status ON raw_items(status);
CREATE INDEX idx_raw_items_source_id ON raw_items(source_id);

-- Stories table
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_item_id UUID REFERENCES raw_items(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN (
        'AI & Automation Takeovers',
        'Corporate Collapses & Reversals',
        'Tech Decisions With Massive Fallout',
        'Laws & Rules That Quietly Changed Everything',
        'Money & Market Shock'
    )),
    shock_score INTEGER NOT NULL CHECK (shock_score >= 0 AND shock_score <= 100),
    factors_json JSONB,
    status TEXT NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED', 'REJECTED', 'APPROVED', 'RENDERED', 'PUBLISHED')),
    decision_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stories_status ON stories(status);
CREATE INDEX idx_stories_category ON stories(category);
CREATE INDEX idx_stories_shock_score ON stories(shock_score);

-- Scripts table
CREATE TABLE IF NOT EXISTS scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    hook TEXT NOT NULL,
    what_happened TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    what_happens_next TEXT NOT NULL,
    cta_line TEXT NOT NULL,
    duration_target_seconds INTEGER DEFAULT 35,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scripts_story_id ON scripts(story_id);

-- Review queue table
CREATE TABLE IF NOT EXISTS review_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    edited_hook TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_queue_status ON review_queue(status);

-- Renders table
CREATE TABLE IF NOT EXISTS renders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    template TEXT NOT NULL CHECK (template IN ('A', 'B', 'C')),
    background_type TEXT NOT NULL CHECK (background_type IN ('STILL', 'MOTION')),
    background_id TEXT NOT NULL,
    output_url TEXT,
    render_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (render_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    ffmpeg_log TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_renders_status ON renders(render_status);
CREATE INDEX idx_renders_background ON renders(background_type, background_id);

-- Publishes table
CREATE TABLE IF NOT EXISTS publishes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    render_id UUID REFERENCES renders(id) ON DELETE CASCADE,
    platform TEXT NOT NULL CHECK (platform IN ('YOUTUBE', 'RUMBLE')),
    platform_video_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    publish_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (publish_status IN ('PENDING', 'UPLOADING', 'PUBLISHED', 'FAILED')),
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_publishes_status ON publishes(publish_status);
CREATE INDEX idx_publishes_platform ON publishes(platform);

-- Analytics daily table
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_video_id TEXT NOT NULL,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    avg_watch_time REAL,
    completion_rate REAL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_video_id, date)
);

CREATE INDEX idx_analytics_video_id ON analytics_daily(platform_video_id);
CREATE INDEX idx_analytics_date ON analytics_daily(date);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
    ('review_mode', '{"enabled": false}'::jsonb),
    ('auto_approve_minutes', '{"value": 60}'::jsonb),
    ('shock_score_threshold', '{"value": 65}'::jsonb),
    ('daily_video_cap', '{"value": 10}'::jsonb),
    ('youtube_visibility', '{"value": "public"}'::jsonb),
    ('enable_rumble', '{"enabled": false}'::jsonb),
    ('background_random_mode', '{"mode": "uniform"}'::jsonb)
ON CONFLICT (key) DO NOTHING;

