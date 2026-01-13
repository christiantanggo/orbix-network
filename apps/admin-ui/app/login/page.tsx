'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Check Supabase configuration on mount
  useEffect(() => {
    // Try to access Supabase URL from the client
    // If it's not configured, the URL will be empty
    const testConnection = async () => {
      try {
        const { data, error } = await supabase.auth.getSession()
        // If we get an error about missing URL/key, it's a config issue
        if (error && (error.message.includes('Invalid API key') || error.message.includes('Invalid URL'))) {
          setError('⚠️ Supabase is not properly configured. Please check your Vercel environment variables (NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY).')
        }
      } catch (err: any) {
        // Connection errors might indicate missing config
        if (err.message && (err.message.includes('fetch') || err.message.includes('Failed to fetch'))) {
          setError('⚠️ Cannot connect to Supabase. Please verify your NEXT_PUBLIC_SUPABASE_URL is correct.')
        }
      }
    }
    testConnection()
  }, [])

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Check if Supabase is configured
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseKey) {
      setError('Supabase is not configured. Please check environment variables.')
      setLoading(false)
      return
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        // Provide more helpful error messages
        if (error.message.includes('Invalid login credentials')) {
          setError('Invalid email or password. Please check your credentials.')
        } else if (error.message.includes('Email not confirmed')) {
          setError('Please confirm your email before logging in.')
        } else if (error.message.includes('Too many requests')) {
          setError('Too many login attempts. Please try again later.')
        } else {
          setError(error.message || 'An error occurred during login. Please check your Supabase configuration.')
        }
        setLoading(false)
      } else if (data?.user) {
        router.push('/dashboard')
      } else {
        setError('Login failed. Please try again.')
        setLoading(false)
      }
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.message || 'An unexpected error occurred. Please check your network connection and Supabase configuration.')
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Orbix Network Admin</h1>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onInput={(e) => setEmail((e.target as HTMLInputElement).value)}
              required
              autoComplete="off"
              data-testid="email-input"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onInput={(e) => setPassword((e.target as HTMLInputElement).value)}
              required
              autoComplete="new-password"
              data-testid="password-input"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
            />
          </div>
          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}
