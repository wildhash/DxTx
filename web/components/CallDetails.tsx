'use client'

import { useState, useEffect } from 'react'
import { PhoneOff, FileText, User, Calendar, Clock } from 'lucide-react'
import { format } from 'date-fns'

interface CallDetailsProps {
  callId: string
}

interface CallData {
  id: number
  call_id: string
  direction: string
  status: string
  phone_number: string
  patient_name: string | null
  started_at: string
  answered_at: string | null
  ended_at: string | null
  duration_seconds: number | null
  transcript: string | null
  ai_summary: string | null
  extracted_data: any
}

interface TranscriptEntry {
  speaker: string
  text: string
  timestamp: string
  confidence: number
}

export default function CallDetails({ callId }: CallDetailsProps) {
  const [call, setCall] = useState<CallData | null>(null)
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'details' | 'transcript' | 'summary'>('details')

  useEffect(() => {
    fetchCallDetails()
    fetchTranscript()
  }, [callId])

  const fetchCallDetails = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/calls/${callId}`)
      if (response.ok) {
        const data = await response.json()
        setCall(data)
      }
    } catch (error) {
      console.error('Error fetching call details:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTranscript = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/transcripts/${callId}`)
      if (response.ok) {
        const data = await response.json()
        setTranscript(data.entries || [])
      }
    } catch (error) {
      // Transcript may not exist yet
      console.log('No transcript available yet')
    }
  }

  const handleHangup = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/calls/${callId}/hangup`,
        { method: 'POST' }
      )
      if (response.ok) {
        fetchCallDetails()
      }
    } catch (error) {
      console.error('Error hanging up call:', error)
    }
  }

  if (loading || !call) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-center text-gray-500">Loading...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-lg font-medium text-gray-900">
              {call.patient_name || 'Unknown'}
            </h2>
            <p className="text-sm text-gray-500">{call.phone_number}</p>
          </div>
          {(call.status === 'in_progress' || call.status === 'answered') && (
            <button
              onClick={handleHangup}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
            >
              <PhoneOff className="h-4 w-4 mr-1" />
              End Call
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          {['details', 'transcript', 'summary'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === tab
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'details' && (
          <div className="space-y-4">
            <div className="flex items-center text-sm">
              <User className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-500">Direction:</span>
              <span className="ml-2 font-medium capitalize">{call.direction}</span>
            </div>
            <div className="flex items-center text-sm">
              <Clock className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-500">Status:</span>
              <span className="ml-2 font-medium capitalize">{call.status}</span>
            </div>
            <div className="flex items-center text-sm">
              <Calendar className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-500">Started:</span>
              <span className="ml-2 font-medium">
                {format(new Date(call.started_at), 'PPpp')}
              </span>
            </div>
            {call.duration_seconds !== null && (
              <div className="flex items-center text-sm">
                <Clock className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-500">Duration:</span>
                <span className="ml-2 font-medium">
                  {Math.floor(call.duration_seconds / 60)}m {call.duration_seconds % 60}s
                </span>
              </div>
            )}
            {call.extracted_data && Object.keys(call.extracted_data).length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Extracted Data</h3>
                <dl className="space-y-2">
                  {Object.entries(call.extracted_data).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <dt className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</dt>
                      <dd className="mt-1 text-gray-900">{String(value)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
          </div>
        )}

        {activeTab === 'transcript' && (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {transcript.length === 0 ? (
              <p className="text-sm text-gray-500 text-center">No transcript available</p>
            ) : (
              transcript.map((entry, index) => (
                <div
                  key={index}
                  className={`flex ${
                    entry.speaker === 'agent' ? 'justify-start' : 'justify-end'
                  }`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      entry.speaker === 'agent'
                        ? 'bg-gray-100 text-gray-900'
                        : 'bg-primary-600 text-white'
                    }`}
                  >
                    <p className="text-sm">{entry.text}</p>
                    <p className="text-xs mt-1 opacity-75">
                      {format(new Date(entry.timestamp), 'HH:mm:ss')}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div>
            {call.ai_summary ? (
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{call.ai_summary}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center">
                Summary will be available after the call ends
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
