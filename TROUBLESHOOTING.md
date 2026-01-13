# Troubleshooting Guide

## Supabase Auth Errors

### Error: 500 from `/auth/v1/token?grant_type=password`

This error typically indicates a Supabase configuration issue. Here's how to fix it:

#### 1. Check Environment Variables in Vercel

Make sure you have set the following environment variables in your Vercel project:

1. Go to your Vercel project: https://vercel.com/christian-fourniers-projects/admin-ui/settings/environment-variables
2. Add these variables:
   - `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon/public key

#### 2. Get Your Supabase Credentials

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → Use for `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → Use for `NEXT_PUBLIC_SUPABASE_ANON_KEY`

#### 3. Verify Your Supabase Project is Active

- Check if your Supabase project is active (not paused)
- Ensure your project hasn't exceeded its free tier limits
- Verify the project URL is correct

#### 4. Redeploy After Adding Environment Variables

After adding environment variables in Vercel:
1. Go to your Vercel project
2. Click **Deployments**
3. Click the three dots (...) on the latest deployment
4. Click **Redeploy** (or it will auto-deploy on next push)

#### 5. Check User Exists in Supabase

1. Go to Supabase Dashboard → **Authentication** → **Users**
2. Verify the user you're trying to log in with exists
3. If using `add_user.sql`, make sure you've run it in the Supabase SQL Editor

#### 6. Common Issues

- **Wrong URL format**: Should be `https://xxxxx.supabase.co` (not `https://xxxxx.supabase.co/`)
- **Wrong key**: Make sure you're using the **anon** key, not the **service_role** key
- **Missing variables**: Both `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` must be set
- **Variables not synced**: After adding variables, you must redeploy

### Error: 404 Not Found

This usually means:
- A route/page doesn't exist
- A static asset is missing
- The build didn't complete successfully

Check the Vercel deployment logs to see what resource is missing.

## Testing Locally

To test the Supabase connection locally:

1. Create a `.env.local` file in `apps/admin-ui/`:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

2. Run `npm run dev` in the `apps/admin-ui` directory

3. Try logging in and check the browser console for errors

## Verifying Environment Variables Are Set

You can check if environment variables are available by looking at the browser console. The app will log errors if Supabase is not properly configured.

