import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { reviewService, meetingService } from '../services/api'
import StarRating from '../components/StarRating'
import type { Review, Meeting } from '../types'

const StudyingDashboard = () => {
  const { user } = useAuth()
  const [reviews, setReviews] = useState<Review[]>([])
  const [invitations, setInvitations] = useState<Meeting[]>([])
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [reviewFormData, setReviewFormData] = useState({
    unique_key: user?.unique_key || '',
    teaching_rating: 5,
    teaching_review: '',
    courses_rating: 5,
    courses_review: '',
    library_rating: 5,
    library_review: '',
    research_rating: 5,
    research_review: '',
    internship_rating: 5,
    internship_review: '',
    infrastructure_rating: 5,
    infrastructure_review: '',
    administration_rating: 5,
    administration_review: '',
    extracurricular_rating: 5,
    extracurricular_review: '',
    safety_rating: 5,
    safety_review: '',
    placement_rating: 5,
    placement_review: '',
    preferred_day: '',
    preferred_time: '',
  })

  useEffect(() => {
    loadInvitations()
  }, [])

  const loadInvitations = async () => {
    try {
      const data = await meetingService.myInvitations()
      setInvitations(data.filter(m => m.status === 'requested'))
    } catch (err) {
      console.error('Error loading invitations:', err)
    }
  }

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await reviewService.create(reviewFormData)
      alert('Review submitted successfully!')
      setShowReviewForm(false)
      setReviewFormData({
        unique_key: user?.unique_key || '',
        teaching_rating: 5,
        teaching_review: '',
        courses_rating: 5,
        courses_review: '',
        library_rating: 5,
        library_review: '',
        research_rating: 5,
        research_review: '',
        internship_rating: 5,
        internship_review: '',
        infrastructure_rating: 5,
        infrastructure_review: '',
        administration_rating: 5,
        administration_review: '',
        extracurricular_rating: 5,
        extracurricular_review: '',
        safety_rating: 5,
        safety_review: '',
        placement_rating: 5,
        placement_review: '',
        preferred_day: '',
        preferred_time: '',
      })
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error submitting review')
    }
  }

  const handleMeetingStatus = async (meetingId: number, status: string) => {
    try {
      await meetingService.updateStatus(meetingId, status)
      await loadInvitations()
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error updating meeting status')
    }
  }

  const ratingFields = [
    { key: 'teaching', label: 'Teaching Quality' },
    { key: 'courses', label: 'Course Curriculum' },
    { key: 'library', label: 'Library Facilities' },
    { key: 'research', label: 'Research Opportunities' },
    { key: 'internship', label: 'Internship Support' },
    { key: 'infrastructure', label: 'Infrastructure' },
    { key: 'administration', label: 'Administration' },
    { key: 'extracurricular', label: 'Extracurricular Activities' },
    { key: 'safety', label: 'Safety & Security' },
    { key: 'placement', label: 'Placement Support' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Studying Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome, {user?.email_id}
        </p>
        {user?.unique_key && (
          <p className="text-sm text-gray-500">
            Branch: {user.unique_key} | Year: {user.year_of_starting}
          </p>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <button
            onClick={() => setShowReviewForm(!showReviewForm)}
            className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
          >
            {showReviewForm ? 'Cancel Review' : 'Submit Review'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">
            Meeting Requests ({invitations.length})
          </h2>
          {invitations.length === 0 ? (
            <p className="text-gray-500">No pending requests</p>
          ) : (
            <div className="space-y-2">
              {invitations.map(meeting => (
                <div key={meeting.meeting_id} className="p-3 bg-gray-50 rounded">
                  <p className="text-sm">Request from: {meeting.counselling_user_id}</p>
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => handleMeetingStatus(meeting.meeting_id, 'accepted')}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleMeetingStatus(meeting.meeting_id, 'rejected')}
                      className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showReviewForm && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Submit Review</h2>
          <form onSubmit={handleReviewSubmit} className="space-y-6">
            {ratingFields.map(field => (
              <div key={field.key}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                </label>
                <StarRating
                  rating={reviewFormData[`${field.key}_rating` as keyof typeof reviewFormData] as number}
                  onRatingChange={(rating) =>
                    setReviewFormData(prev => ({
                      ...prev,
                      [`${field.key}_rating`]: rating,
                    }))
                  }
                />
                <textarea
                  placeholder={`${field.label} review...`}
                  value={reviewFormData[`${field.key}_review` as keyof typeof reviewFormData] as string}
                  onChange={(e) =>
                    setReviewFormData(prev => ({
                      ...prev,
                      [`${field.key}_review`]: e.target.value,
                    }))
                  }
                  className="mt-2 w-full px-3 py-2 border rounded-md"
                  rows={2}
                />
              </div>
            ))}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Day for Meetings
                </label>
                <input
                  type="text"
                  value={reviewFormData.preferred_day}
                  onChange={(e) =>
                    setReviewFormData(prev => ({ ...prev, preferred_day: e.target.value }))
                  }
                  placeholder="e.g., Monday, Wednesday"
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Time for Meetings
                </label>
                <input
                  type="text"
                  value={reviewFormData.preferred_time}
                  onChange={(e) =>
                    setReviewFormData(prev => ({ ...prev, preferred_time: e.target.value }))
                  }
                  placeholder="e.g., 6 PM - 8 PM"
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
            >
              Submit Review
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default StudyingDashboard

