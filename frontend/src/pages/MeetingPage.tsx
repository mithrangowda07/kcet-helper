import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { meetingService } from '../services/api'
import type { Meeting } from '../types'

const MeetingPage = () => {
  const { user } = useAuth()
  const [requests, setRequests] = useState<Meeting[]>([])
  const [invitations, setInvitations] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadMeetings()
  }, [])

  const loadMeetings = async () => {
    setLoading(true)
    try {
      if (user?.type_of_student === 'counselling') {
        const data = await meetingService.myRequests()
        setRequests(data)
      } else {
        const data = await meetingService.myInvitations()
        setInvitations(data)
      }
    } catch (err) {
      console.error('Error loading meetings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (meetingId: number, status: string) => {
    try {
      await meetingService.updateStatus(meetingId, status)
      await loadMeetings()
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error updating meeting status')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold mb-6">Meetings</h1>

      {user?.type_of_student === 'counselling' && (
        <div>
          <h2 className="text-xl font-semibold mb-4">My Meeting Requests</h2>
          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : requests.length === 0 ? (
            <div className="bg-white p-6 rounded-lg shadow-md text-center text-gray-500">
              No meeting requests yet
            </div>
          ) : (
            <div className="space-y-4">
              {requests.map(meeting => (
                <div key={meeting.meeting_id} className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">Meeting with: {meeting.studying_user_id}</p>
                      <p className="text-sm text-gray-600">
                        Status: <span className={`px-2 py-1 rounded ${getStatusColor(meeting.status)}`}>
                          {meeting.status}
                        </span>
                      </p>
                      {meeting.scheduled_time && (
                        <p className="text-sm text-gray-600">
                          Scheduled: {new Date(meeting.scheduled_time).toLocaleString()}
                        </p>
                      )}
                      {meeting.meet_link && (
                        <a
                          href={meeting.meet_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:underline text-sm mt-2 inline-block"
                        >
                          Join Google Meet
                        </a>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {meeting.status === 'accepted' && (
                        <button
                          onClick={() => handleStatusUpdate(meeting.meeting_id, 'completed')}
                          className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                        >
                          Mark Completed
                        </button>
                      )}
                      {['requested', 'accepted'].includes(meeting.status) && (
                        <button
                          onClick={() => handleStatusUpdate(meeting.meeting_id, 'cancelled')}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {user?.type_of_student === 'studying' && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Meeting Invitations</h2>
          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : invitations.length === 0 ? (
            <div className="bg-white p-6 rounded-lg shadow-md text-center text-gray-500">
              No meeting invitations
            </div>
          ) : (
            <div className="space-y-4">
              {invitations.map(meeting => (
                <div key={meeting.meeting_id} className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">Request from: {meeting.counselling_user_id}</p>
                      <p className="text-sm text-gray-600">
                        Status: <span className={`px-2 py-1 rounded ${getStatusColor(meeting.status)}`}>
                          {meeting.status}
                        </span>
                      </p>
                      {meeting.scheduled_time && (
                        <p className="text-sm text-gray-600">
                          Scheduled: {new Date(meeting.scheduled_time).toLocaleString()}
                        </p>
                      )}
                      {meeting.meet_link && (
                        <a
                          href={meeting.meet_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:underline text-sm mt-2 inline-block"
                        >
                          Join Google Meet
                        </a>
                      )}
                    </div>
                    {meeting.status === 'requested' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleStatusUpdate(meeting.meeting_id, 'accepted')}
                          className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(meeting.meeting_id, 'rejected')}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                    {meeting.status === 'accepted' && (
                      <button
                        onClick={() => handleStatusUpdate(meeting.meeting_id, 'completed')}
                        className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                      >
                        Mark Completed
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default MeetingPage

