-- Seed data for Orbix Network

-- Create admin user using Supabase auth
-- Run this in Supabase SQL Editor
-- Note: The easiest way is through Dashboard > Authentication > Users > Add user
-- But if you want SQL, you can use the Supabase Management API or run this:

-- Option 1: Use Supabase Dashboard (RECOMMENDED)
-- Go to: Authentication > Users > Add user
-- Email: christian.fournier@tanggo.ca
-- Password: 1986Cc1991!#
-- Auto Confirm User: ON

-- Option 2: If you must use SQL, you need to enable pgcrypto extension first:
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Then insert (this is complex and may not work due to Supabase's auth system):
-- The password hash format is specific to Supabase's auth system
-- It's safer to use the Dashboard or the Supabase Management API

-- Insert sample sources
INSERT INTO sources (name, url, type, enabled, fetch_interval_minutes) VALUES
    ('TechCrunch RSS', 'https://techcrunch.com/feed/', 'RSS', true, 60),
    ('The Verge RSS', 'https://www.theverge.com/rss/index.xml', 'RSS', true, 60),
    ('Reuters Tech', 'https://www.reuters.com/technology', 'HTML', true, 120)
ON CONFLICT DO NOTHING;

