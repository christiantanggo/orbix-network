# Orbix Network

A fully automated media system that scrapes news, generates scripts, renders videos, and publishes to YouTube Shorts.

## Architecture

- **Supabase**: PostgreSQL database, Authentication, File Storage
- **Railway**: Python worker with FFmpeg for video rendering
- **Vercel**: Next.js admin dashboard

## Setup

### 1. Supabase Setup

1. Create a new Supabase project
2. Run the migration: `supabase/migrations/001_initial_schema.sql`
3. Create a storage bucket named `renders` for video outputs
4. Note your Supabase URL and service role key

### 2. Railway Worker Setup

1. Create a new Railway project
2. Connect your repository
3. Set the root directory to `apps/worker`
4. Add environment variables from `apps/worker/env.example`
5. Install FFmpeg in your Railway environment
6. Deploy

### 3. Vercel Admin UI Setup

1. Create a new Vercel project
2. Connect your repository
3. Set the root directory to `apps/admin-ui`
4. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5. Deploy

### 4. Assets Setup

Place your background assets in:
- `assets/backgrounds/stills/` - 6 still images (JPG)
- `assets/backgrounds/motion/` - 6 motion videos (MP4)
- `assets/logos/` - Orbix watermark (optional)

## Environment Variables

### Worker (Railway)

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_STORAGE_BUCKET=renders
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token
RUMBLE_API_KEY=your_rumble_api_key (optional)
LOG_LEVEL=INFO
```

### Admin UI (Vercel)

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Pipeline Flow

1. **Scraping**: Fetches headlines from RSS/HTML sources every 5 minutes
2. **Classification**: AI classifies stories into 5 categories and scores shock value
3. **Script Generation**: Creates scripts with hook, what happened, why it matters, what happens next, CTA
4. **Review Queue**: Optional human review with auto-approve timer
5. **Rendering**: FFmpeg renders vertical videos (1080x1920) with randomized backgrounds
6. **Publishing**: Uploads to YouTube Shorts (and optionally Rumble)
7. **Analytics**: Collects daily metrics for performance tracking

## Content Categories

1. AI & Automation Takeovers
2. Corporate Collapses & Reversals
3. Tech Decisions With Massive Fallout
4. Laws & Rules That Quietly Changed Everything
5. Money & Market Shock

## Video Style

- Vertical format: 1080x1920
- Duration: 30-45 seconds
- Studio aesthetic (no visible host)
- 12 backgrounds: 6 stills + 6 motion loops
- Random selection at render time
- Calm, authoritative AI voiceover

## Admin Dashboard

Access the admin UI to:
- Manage news sources
- Review and edit scripts
- View render history
- Monitor published videos
- Analyze performance metrics
- Configure system settings

## License

Private - All Rights Reserved

