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

  useEffect(() => {
    // Force text color after component mounts
    const forceTextColor = () => {
      const emailInput = document.getElementById('email') as HTMLInputElement
      const passwordInput = document.getElementById('password') as HTMLInputElement
      
      if (emailInput) {
        emailInput.style.color = '#111827'
        emailInput.style.backgroundColor = '#ffffff'
        emailInput.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
        emailInput.style.setProperty('color', '#111827', 'important')
      }
      
      if (passwordInput) {
        passwordInput.style.color = '#111827'
        passwordInput.style.backgroundColor = '#ffffff'
        passwordInput.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
        passwordInput.style.setProperty('color', '#111827', 'important')
      }
    }

    forceTextColor()
    // Also force on input events
    const interval = setInterval(forceTextColor, 100)
    
    return () => clearInterval(interval)
  }, [])

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      router.push('/dashboard')
    }
  }

  return (
    <>
      <style dangerouslySetInnerHTML={{__html: `
        #email, #password {
          color: #111827 !important;
          background-color: #ffffff !important;
        }
        #email::placeholder, #password::placeholder {
          color: #9ca3af !important;
        }
      `}} />
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
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                const input = e.target as HTMLInputElement
                input.style.color = '#111827'
                input.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
              }}
              onInput={(e) => {
                const input = e.target as HTMLInputElement
                input.style.color = '#111827'
                input.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
              }}
              autoComplete="off"
              required
              style={{ color: '#111827 !important', backgroundColor: '#ffffff !important', WebkitTextFillColor: '#111827' } as any}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                const input = e.target as HTMLInputElement
                input.style.color = '#111827'
                input.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
              }}
              onInput={(e) => {
                const input = e.target as HTMLInputElement
                input.style.color = '#111827'
                input.style.setProperty('-webkit-text-fill-color', '#111827', 'important')
              }}
              autoComplete="new-password"
              required
              style={{ color: '#111827 !important', backgroundColor: '#ffffff !important', WebkitTextFillColor: '#111827' } as any}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
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
    </>
  )
}

