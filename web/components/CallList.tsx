'use client'

import { useState, useEffect } from 'react'
import { Phone, Clock, CheckCircle, XCircle, PhoneOff } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface Call {
  id: number
  call_id: string
  direction: string
  status: string
  phone_number: string
  patient_name: string | null
  started_at: string
  duration_seconds: number | null
}

interface CallListProps {
  onSelectCall: (callId: string) => void
  selectedCallId: string | null
}

export default function CallList({ onSelectCall, selectedCallId }: CallListProps) {
  const [calls, setCalls] = useState<Call[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCalls()
    const interval = setInterval(fetchCalls, 3000) // Refresh every 3 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchCalls = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/calls`)
      if (response.ok) {
        const data = await response.json()
        setCalls(data)
      }
    } catch (error) {
      console.error('Error fetching calls:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'in_progress':
      case 'answered':
        return <Phone className="h-5 w-5 text-blue-500 animate-pulse" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'in_progress':
      case 'answered':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-center text-gray-500">Loading calls...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Recent Calls</h2>
      </div>
      <div className="divide-y divide-gray-200">
        {calls.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <PhoneOff className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p>No calls yet</p>
          </div>
        ) : (
          calls.map((call) => (
            <div
              key={call.call_id}
              onClick={() => onSelectCall(call.call_id)}
              className={`p-4 hover:bg-gray-50 cursor-pointer transition ${
                selectedCallId === call.call_id ? 'bg-primary-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 pt-1">
                    {getStatusIcon(call.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {call.patient_name || call.phone_number}
                    </p>
                    <p className="text-sm text-gray-500">
                      {call.phone_number}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDistanceToNow(new Date(call.started_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                      call.status
                    )}`}
                  >
                    {call.status}
                  </span>
                  {call.duration_seconds !== null && (
                    <span className="text-xs text-gray-500">
                      {Math.floor(call.duration_seconds / 60)}m {call.duration_seconds % 60}s
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
