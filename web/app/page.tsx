'use client'

import { useState, useEffect } from 'react'
import { Phone, PhoneCall, PhoneOff, Activity, Users, CheckCircle, XCircle } from 'lucide-react'
import CallList from '@/components/CallList'
import CallDetails from '@/components/CallDetails'
import NewCallModal from '@/components/NewCallModal'
import StatsCards from '@/components/StatsCards'

export default function Home() {
  const [showNewCallModal, setShowNewCallModal] = useState(false)
  const [selectedCallId, setSelectedCallId] = useState<string | null>(null)
  const [stats, setStats] = useState({
    total_calls: 0,
    active_calls: 0,
    completed_calls: 0,
    failed_calls: 0,
  })

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/stats`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Phone className="h-8 w-8 text-primary-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">DxTx Dashboard</h1>
            </div>
            <button
              onClick={() => setShowNewCallModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PhoneCall className="h-5 w-5 mr-2" />
              New Call
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <StatsCards stats={stats} />

        {/* Content Grid */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Call List */}
          <div className="lg:col-span-2">
            <CallList onSelectCall={setSelectedCallId} selectedCallId={selectedCallId} />
          </div>

          {/* Call Details */}
          <div className="lg:col-span-1">
            {selectedCallId ? (
              <CallDetails callId={selectedCallId} />
            ) : (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                <Phone className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>Select a call to view details</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* New Call Modal */}
      {showNewCallModal && (
        <NewCallModal
          onClose={() => setShowNewCallModal(false)}
          onCallCreated={() => {
            setShowNewCallModal(false)
            // Refresh call list
          }}
        />
      )}
    </div>
  )
}
