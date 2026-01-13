'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkUser()
    loadStats()
  }, [])

  async function checkUser() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/login')
    } else {
      setUser(user)
    }
  }

  async function loadStats() {
    try {
      // Get pipeline stats
      const [rawItems, stories, renders, publishes] = await Promise.all([
        supabase.from('raw_items').select('id', { count: 'exact', head: true }),
        supabase.from('stories').select('id', { count: 'exact', head: true }),
        supabase.from('renders').select('id', { count: 'exact', head: true }),
        supabase.from('publishes').select('id', { count: 'exact', head: true }),
      ])

      setStats({
        rawItems: rawItems.count || 0,
        stories: stories.count || 0,
        renders: renders.count || 0,
        publishes: publishes.count || 0,
      })
    } catch (error) {
      console.error('Error loading stats:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut()
    router.push('/login')
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Orbix Network Admin</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-indigo-600 hover:text-indigo-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Raw Items</h3>
            <p className="text-2xl font-bold mt-2">{stats?.rawItems || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Stories</h3>
            <p className="text-2xl font-bold mt-2">{stats?.stories || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Renders</h3>
            <p className="text-2xl font-bold mt-2">{stats?.renders || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Published</h3>
            <p className="text-2xl font-bold mt-2">{stats?.publishes || 0}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link href="/sources" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Sources Manager</h3>
            <p className="text-sm text-gray-600">Manage news sources</p>
          </Link>
          <Link href="/review" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Review Queue</h3>
            <p className="text-sm text-gray-600">Approve or edit scripts</p>
          </Link>
          <Link href="/renders" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Render History</h3>
            <p className="text-sm text-gray-600">View rendered videos</p>
          </Link>
          <Link href="/published" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Published Videos</h3>
            <p className="text-sm text-gray-600">View published content</p>
          </Link>
          <Link href="/analytics" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Analytics</h3>
            <p className="text-sm text-gray-600">Performance metrics</p>
          </Link>
          <Link href="/settings" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold mb-2">Settings</h3>
            <p className="text-sm text-gray-600">System configuration</p>
          </Link>
        </div>
      </main>
    </div>
  )
}

