-- Add admin user to Supabase
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard > SQL Editor

-- Enable pgcrypto extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Insert user into auth.users
-- Note: Supabase uses bcrypt for password hashing
-- Check if user already exists first
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM auth.users WHERE email = 'christian.fournier@tanggo.ca'
    ) THEN
        INSERT INTO auth.users (
            instance_id,
            id,
            aud,
            role,
            email,
            encrypted_password,
            email_confirmed_at,
            created_at,
            updated_at,
            raw_app_meta_data,
            raw_user_meta_data,
            is_super_admin,
            confirmation_token,
            recovery_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            gen_random_uuid(),
            'authenticated',
            'authenticated',
            'christian.fournier@tanggo.ca',
            crypt('1986Cc1991!#', gen_salt('bf')),
            now(),
            now(),
            now(),
            '{"provider":"email","providers":["email"]}',
            '{}',
            false,
            '',
            ''
        );
    ELSE
        RAISE NOTICE 'User already exists';
    END IF;
END $$;

