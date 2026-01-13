-- Seed data for Orbix Network

-- Insert sample sources
INSERT INTO sources (name, url, type, enabled, fetch_interval_minutes) VALUES
    ('TechCrunch RSS', 'https://techcrunch.com/feed/', 'RSS', true, 60),
    ('The Verge RSS', 'https://www.theverge.com/rss/index.xml', 'RSS', true, 60),
    ('Reuters Tech', 'https://www.reuters.com/technology', 'HTML', true, 120)
ON CONFLICT DO NOTHING;

