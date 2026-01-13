'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'

export default function SettingsPage() {
  const router = useRouter()
  const [settings, setSettings] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    checkUser()
    loadSettings()
  }, [])

  async function checkUser() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/login')
    }
  }

  async function loadSettings() {
    const { data, error } = await supabase.from('settings').select('*')
    if (data) {
      const settingsObj: any = {}
      data.forEach((s: any) => {
        settingsObj[s.key] = s.value
      })
      setSettings(settingsObj)
    }
    setLoading(false)
  }

  async function saveSetting(key: string, value: any) {
    setSaving(true)
    const { error } = await supabase
      .from('settings')
      .upsert({ key, value, updated_at: new Date().toISOString() })
    
    if (!error) {
      setSettings({ ...settings, [key]: value })
    }
    setSaving(false)
  }

  function updateSetting(key: string, value: any) {
    setSettings({ ...settings, [key]: value })
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
              <h1 className="text-xl font-bold">Settings</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Review Mode
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.review_mode?.enabled || false}
                onChange={(e) => {
                  updateSetting('review_mode', { enabled: e.target.checked })
                  saveSetting('review_mode', { enabled: e.target.checked })
                }}
                className="mr-2"
              />
              <span>Enable human review before rendering</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-approve Minutes
            </label>
            <input
              type="number"
              value={settings.auto_approve_minutes?.value || 60}
              onChange={(e) => updateSetting('auto_approve_minutes', { value: parseInt(e.target.value) })}
              onBlur={() => saveSetting('auto_approve_minutes', settings.auto_approve_minutes)}
              className="px-3 py-2 border border-gray-300 rounded-md w-32"
            />
            <p className="text-sm text-gray-500 mt-1">Minutes before auto-approving pending reviews</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Shock Score Threshold
            </label>
            <input
              type="number"
              value={settings.shock_score_threshold?.value || 65}
              onChange={(e) => updateSetting('shock_score_threshold', { value: parseInt(e.target.value) })}
              onBlur={() => saveSetting('shock_score_threshold', settings.shock_score_threshold)}
              className="px-3 py-2 border border-gray-300 rounded-md w-32"
            />
            <p className="text-sm text-gray-500 mt-1">Minimum shock score (0-100) to process a story</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Daily Video Cap
            </label>
            <input
              type="number"
              value={settings.daily_video_cap?.value || 10}
              onChange={(e) => updateSetting('daily_video_cap', { value: parseInt(e.target.value) })}
              onBlur={() => saveSetting('daily_video_cap', settings.daily_video_cap)}
              className="px-3 py-2 border border-gray-300 rounded-md w-32"
            />
            <p className="text-sm text-gray-500 mt-1">Maximum videos to publish per day</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              YouTube Visibility
            </label>
            <select
              value={settings.youtube_visibility?.value || 'public'}
              onChange={(e) => {
                updateSetting('youtube_visibility', { value: e.target.value })
                saveSetting('youtube_visibility', { value: e.target.value })
              }}
              className="px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="public">Public</option>
              <option value="unlisted">Unlisted</option>
              <option value="private">Private</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enable Rumble
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.enable_rumble?.enabled || false}
                onChange={(e) => {
                  updateSetting('enable_rumble', { enabled: e.target.checked })
                  saveSetting('enable_rumble', { enabled: e.target.checked })
                }}
                className="mr-2"
              />
              <span>Enable Rumble publishing</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Background Random Mode
            </label>
            <select
              value={settings.background_random_mode?.mode || 'uniform'}
              onChange={(e) => {
                updateSetting('background_random_mode', { mode: e.target.value })
                saveSetting('background_random_mode', { mode: e.target.value })
              }}
              className="px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="uniform">Uniform (50/50)</option>
              <option value="weighted">Weighted</option>
            </select>
          </div>
        </div>
      </main>
    </div>
  )
}

