# Orbix Network Setup Guide

## Prerequisites

1. **Supabase Account**: Create a project at https://supabase.com
2. **Railway Account**: For running the Python worker
3. **Vercel Account**: For hosting the admin UI
4. **OpenAI API Key**: For AI classification and script generation
5. **YouTube API Credentials**: For publishing videos
6. **FFmpeg**: Must be installed in Railway environment

## Step 1: Supabase Setup

1. Create a new Supabase project
2. Go to SQL Editor and run `supabase/migrations/001_initial_schema.sql`
3. (Optional) Run `supabase/seed.sql` to add sample sources
4. Go to Storage and create a bucket named `renders` (public)
5. Note your:
   - Project URL
   - Service Role Key (for worker)
   - Anon Key (for admin UI)

## Step 2: Railway Worker Setup

1. Create a new Railway project
2. Connect your GitHub repository
3. Set root directory to `apps/worker`
4. Add a service with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
5. Add environment variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_service_role_key
   SUPABASE_STORAGE_BUCKET=renders
   OPENAI_API_KEY=your_openai_api_key
   YOUTUBE_CLIENT_ID=your_youtube_client_id
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
   YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token
   LOG_LEVEL=INFO
   ```
6. Install FFmpeg in Railway (add to build command or use Nixpacks)
7. Deploy

## Step 3: Vercel Admin UI Setup

1. Create a new Vercel project
2. Connect your GitHub repository
3. Set root directory to `apps/admin-ui`
4. Framework preset: Next.js
5. Add environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
6. Deploy

## Step 4: Assets Setup

1. Add 6 still background images to `assets/backgrounds/stills/`:
   - bg_still_1.jpg through bg_still_6.jpg
2. Add 6 looping motion videos to `assets/backgrounds/motion/`:
   - bg_motion_1.mp4 through bg_motion_6.mp4
3. (Optional) Add watermark to `assets/logos/orbix_watermark.png`
4. Add font files to `assets/fonts/` for text rendering

## Step 5: YouTube API Setup

1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Generate refresh token using OAuth flow
6. Add credentials to Railway environment variables

## Step 6: Initial Configuration

1. Access your admin UI at your Vercel URL
2. Log in with Supabase Auth (create account first)
3. Go to Settings and configure:
   - Review mode (enable/disable)
   - Auto-approve minutes
   - Shock score threshold
   - Daily video cap
   - YouTube visibility
4. Go to Sources Manager and add/edit news sources

## Testing

1. Check Railway logs to ensure worker is running
2. Verify sources are being scraped (check raw_items table)
3. Check stories are being created (check stories table)
4. Monitor review queue if review mode is enabled
5. Check renders are being created and processed
6. Verify videos are being published to YouTube

## Troubleshooting

- **Worker not starting**: Check Railway logs, verify environment variables
- **No stories created**: Check OpenAI API key, verify classification threshold
- **Renders failing**: Check FFmpeg installation, verify background assets exist
- **Publishing failing**: Verify YouTube API credentials and refresh token
- **Admin UI not loading**: Check Supabase connection, verify environment variables

## Next Steps

- Monitor the pipeline through the admin dashboard
- Adjust settings based on performance
- Add more news sources as needed
- Customize video templates and backgrounds
- Review analytics to optimize content

