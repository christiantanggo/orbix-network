'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'

export default function ReviewPage() {
  const router = useRouter()
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editedHook, setEditedHook] = useState('')

  useEffect(() => {
    checkUser()
    loadReviewQueue()
  }, [])

  async function checkUser() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/login')
    }
  }

  async function loadReviewQueue() {
    const { data, error } = await supabase
      .from('review_queue')
      .select('*, stories(*, raw_items(*)), scripts(*)')
      .eq('status', 'PENDING')
      .order('created_at', { ascending: true })
    
    if (data) {
      setItems(data)
    }
    setLoading(false)
  }

  async function approveItem(id: string) {
    const { error } = await supabase
      .from('review_queue')
      .update({ 
        status: 'APPROVED',
        reviewed_at: new Date().toISOString()
      })
      .eq('id', id)
    
    if (!error) {
      // Update story status
      const item = items.find(i => i.id === id)
      if (item) {
        await supabase
          .from('stories')
          .update({ status: 'APPROVED' })
          .eq('id', item.story_id)
      }
      loadReviewQueue()
    }
  }

  async function rejectItem(id: string) {
    const { error } = await supabase
      .from('review_queue')
      .update({ 
        status: 'REJECTED',
        reviewed_at: new Date().toISOString()
      })
      .eq('id', id)
    
    if (!error) {
      // Update story status
      const item = items.find(i => i.id === id)
      if (item) {
        await supabase
          .from('stories')
          .update({ status: 'REJECTED' })
          .eq('id', item.story_id)
      }
      loadReviewQueue()
    }
  }

  async function saveEditedHook(id: string) {
    const { error } = await supabase
      .from('review_queue')
      .update({ edited_hook: editedHook })
      .eq('id', id)
    
    if (!error) {
      setEditingId(null)
      loadReviewQueue()
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
              <h1 className="text-xl font-bold">Review Queue</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {items.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <p className="text-gray-500">No items pending review</p>
          </div>
        ) : (
          <div className="space-y-6">
            {items.map((item) => {
              const story = item.stories
              const script = item.scripts
              const rawItem = story?.raw_items
              
              return (
                <div key={item.id} className="bg-white p-6 rounded-lg shadow">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold">{rawItem?.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{story?.category} • Score: {story?.shock_score}</p>
                  </div>
                  
                  <div className="space-y-3 mb-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Hook</label>
                      {editingId === item.id ? (
                        <div className="mt-1 flex space-x-2">
                          <input
                            type="text"
                            value={editedHook}
                            onChange={(e) => setEditedHook(e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                            defaultValue={script?.hook}
                          />
                          <button
                            onClick={() => saveEditedHook(item.id)}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <p className="mt-1 text-gray-900">{script?.hook}</p>
                      )}
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">What Happened</label>
                      <p className="mt-1 text-gray-900">{script?.what_happened}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Why It Matters</label>
                      <p className="mt-1 text-gray-900">{script?.why_it_matters}</p>
                    </div>
                  </div>
                  
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setEditingId(item.id)
                        setEditedHook(script?.hook || '')
                      }}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                    >
                      Edit Hook
                    </button>
                    <button
                      onClick={() => approveItem(item.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => rejectItem(item.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}

