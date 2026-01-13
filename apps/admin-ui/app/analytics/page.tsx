'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'

export default function AnalyticsPage() {
  const router = useRouter()
  const [analytics, setAnalytics] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [comparisons, setComparisons] = useState<any>(null)

  useEffect(() => {
    checkUser()
    loadAnalytics()
    loadComparisons()
  }, [])

  async function checkUser() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/login')
    }
  }

  async function loadAnalytics() {
    const { data, error } = await supabase
      .from('analytics_daily')
      .select('*')
      .order('date', { ascending: false })
      .limit(100)
    
    if (data) {
      setAnalytics(data)
    }
    setLoading(false)
  }

  async function loadComparisons() {
    // Compare still vs motion backgrounds
    const { data: renders } = await supabase
      .from('renders')
      .select('background_type, background_id, id')
      .eq('render_status', 'COMPLETED')
    
    if (renders) {
      const stillCount = renders.filter(r => r.background_type === 'STILL').length
      const motionCount = renders.filter(r => r.background_type === 'MOTION').length
      
      // Get analytics for each type
      const stillIds = renders.filter(r => r.background_type === 'STILL').map(r => r.id)
      const motionIds = renders.filter(r => r.background_type === 'MOTION').map(r => r.id)
      
      setComparisons({
        still: { count: stillCount },
        motion: { count: motionCount }
      })
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-800">← Back</Link>
              <h1 className="text-xl font-bold">Analytics</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Background Comparison</h3>
            {comparisons && (
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-600">Still Backgrounds: </span>
                  <span className="font-semibold">{comparisons.still.count}</span>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Motion Backgrounds: </span>
                  <span className="font-semibold">{comparisons.motion.count}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Video ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Views</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Likes</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Comments</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Watch Time</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analytics.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 text-sm font-mono">{item.platform_video_id?.substring(0, 12)}...</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(item.date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{item.views || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{item.likes || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{item.comments || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{item.avg_watch_time ? `${item.avg_watch_time}s` : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  )
}

