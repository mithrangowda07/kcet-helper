import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { reviewService, meetingService, branchService } from '../services/api'
import StarRating from '../components/StarRating'
import type { Meeting, Review } from '../types'

const StudyingDashboard = () => {
  const { user } = useAuth()

  const [invitations, setInvitations] = useState<Meeting[]>([])
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [branchName, setBranchName] = useState('')
  const [collegeName, setCollegeName] = useState('')
  const [existingReview, setExistingReview] = useState<Review | null>(null)
  const [submittingReview, setSubmittingReview] = useState(false)

  const daysOfWeek = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
  ]

  // remember the last submitted review so we can edit it
  const reviewFormInit = {
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
  }
  const [reviewFormData, setReviewFormData] = useState(reviewFormInit)

  const selectedDays = reviewFormData.preferred_day
  ? reviewFormData.preferred_day.split(", ").map(d => d.trim())
  : []

  useEffect(() => {
    // load branch display name
    const loadBranch = async () => {
      try {
        if (user?.unique_key) {
          const data = await branchService.detail(user.unique_key)
          setBranchName(data.branch_name || '')
          setCollegeName(data.college.college_name || '')
        } else {
          setBranchName('')
          setCollegeName('')
        }
      } catch (err) {
        console.error('Error loading branch:', err)
        setBranchName('')
        setCollegeName('')
      }
    }

    // load meeting requests
    const loadInvitations = async () => {
      try {
        const data = await meetingService.myInvitations()
        setInvitations(data.filter(m => m.status === 'requested'))
      } catch (err) {
        console.error('Error loading invitations:', err)
      }
    }

    // load existing review
    const loadExistingReview = async () => {
      try {
        if (user?.unique_key) {
          const review = await reviewService.myReview(user.unique_key)
          setExistingReview(review)
          if (review) {
            // Pre-fill form with existing review data
            setReviewFormData({
              unique_key: user.unique_key,
              teaching_rating: review.teaching_rating || 5,
              teaching_review: review.teaching_review || '',
              courses_rating: review.courses_rating || 5,
              courses_review: review.courses_review || '',
              library_rating: review.library_rating || 5,
              library_review: review.library_review || '',
              research_rating: review.research_rating || 5,
              research_review: review.research_review || '',
              internship_rating: review.internship_rating || 5,
              internship_review: review.internship_review || '',
              infrastructure_rating: review.infrastructure_rating || 5,
              infrastructure_review: review.infrastructure_review || '',
              administration_rating: review.administration_rating || 5,
              administration_review: review.administration_review || '',
              extracurricular_rating: review.extracurricular_rating || 5,
              extracurricular_review: review.extracurricular_review || '',
              safety_rating: review.safety_rating || 5,
              safety_review: review.safety_review || '',
              placement_rating: review.placement_rating || 5,
              placement_review: review.placement_review || '',
              preferred_day: review.preferred_day || '',
              preferred_time: review.preferred_time || '',
            })
          } else {
            setReviewFormData(reviewFormInit)
          }
        } else {
          setExistingReview(null)
        }
      } catch (err) {
        console.error('Error loading existing review:', err)
      }
    }

    loadBranch()
    loadInvitations()
    loadExistingReview()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.unique_key])

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submittingReview) return // Prevent multiple submissions
    if (!user?.unique_key) {
      alert('Please set your branch in your profile before submitting a review.')
      return
    }
    
    setSubmittingReview(true)
    try {
      await reviewService.create(reviewFormData)
      alert(existingReview ? 'Review updated successfully!' : 'Review submitted successfully!')
      // Reload existing review
      if (user?.unique_key) {
        const review = await reviewService.myReview(user.unique_key)
        setExistingReview(review)
      }
      setShowReviewForm(false)         // collapse the form after submit
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error submitting review')
    } finally {
      setSubmittingReview(false)
    }
  }

  const handleDeleteReview = async () => {
    if (!user?.unique_key) return
    
    if (!confirm('Are you sure you want to delete your review? This action cannot be undone.')) {
      return
    }

    try {
      await reviewService.delete(user.unique_key)
      setExistingReview(null)
      setReviewFormData(reviewFormInit)
      setShowReviewForm(false)
      alert('Review deleted successfully!')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error deleting review')
    }
  }

  const handleMeetingStatus = async (meetingId: number, status: string) => {
    try {
      await meetingService.updateStatus(meetingId, status)
      const data = await meetingService.myInvitations()
      setInvitations(data.filter(m => m.status === 'requested'))
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
  ] as const

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 dark:text-gray-100">Studying Dashboard</h1>
        <p className="mt-2 text-slate-600 dark:text-gray-400"><span className="font-bold">Welcome,</span> {user?.name || 'User'}</p>
        {user?.unique_key && (
          <>
            <p className="text-sm text-slate-500 dark:text-gray-400">
              <span className="font-bold">College Name :</span> {collegeName || 'Loading...'}
            </p>

            <p className="text-sm text-slate-500 dark:text-gray-400">
              <span className="font-bold">Branch Name :</span> {branchName || 'Loading...'}
            </p>

            <p className='text-sm text-slate-500 dark:text-gray-400'>
              <span className="font-bold">Year of Admission :</span> {user.year_of_starting}
            </p>
          </>
        )}
      </div>

      {/* FIRST: Write / Edit Review */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <h2 className="text-xl font-semibold mb-2 text-slate-800 dark:text-gray-100">
            {existingReview ? 'Edit Your Review' : 'Write a Review'}
          </h2>
          <p className="text-sm text-slate-500 dark:text-gray-400 mb-4">
            {existingReview 
              ? 'Update your review about courses, teaching, placements, and more.'
              : 'Share your experience about courses, teaching, placements, and more.'}
          </p>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setShowReviewForm(v => !v)
              }}
              className="flex-1 bg-slate-500 dark:bg-slate-600 text-white px-4 py-2 rounded-md hover:bg-slate-600 dark:hover:bg-slate-700"
            >
              {showReviewForm ? 'Close' : existingReview ? 'Edit My Review' : 'Write Review'}
            </button>
            {existingReview && (
              <button
                onClick={handleDeleteReview}
                className="bg-red-400 dark:bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-500 dark:hover:bg-red-600"
              >
                Delete My Review
              </button>
            )}
          </div>
        </div>

        {/* Meeting Requests stays second */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-gray-100">
            Meeting Requests ({invitations.length})
          </h2>
          {invitations.length === 0 ? (
            <p className="text-slate-500 dark:text-gray-400">No pending requests</p>
          ) : (
            <div className="space-y-2">
              {invitations.map(meeting => (
                <div key={meeting.meeting_id} className="p-3 bg-slate-50 dark:bg-slate-700 rounded border border-slate-200 dark:border-slate-600">
                  <p className="text-sm text-slate-800 dark:text-gray-200">Request from: {meeting.counselling_user_id}</p>
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

      {/* The review form (opens for Write or Edit) */}
      {showReviewForm && (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-gray-100">
            {existingReview ? 'Edit Your Review' : 'Submit Review'}
          </h2>

          <form onSubmit={handleReviewSubmit} className="space-y-6">
            {ratingFields.map(field => (
              <div key={field.key}>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-2">
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
                  className="mt-2 w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200 placeholder-slate-400 dark:placeholder-gray-500"
                  rows={2}
                />
              </div>
            ))}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1">
                    Preferred Days for Meetings
                  </label>

                  <div className="grid grid-cols-2 gap-2">
                    {daysOfWeek.map(day => (
                      <label key={day} className="flex items-center gap-2 text-slate-700 dark:text-gray-300">
                        <input
                          type="checkbox"
                          checked={selectedDays.includes(day)}
                          onChange={() => {
                            let updatedDays;

                            if (selectedDays.includes(day)) {
                              // remove day
                              updatedDays = selectedDays.filter(d => d !== day);
                            } else {
                              // add day
                              updatedDays = [...selectedDays, day];
                            }

                            setReviewFormData(prev => ({
                              ...prev,
                              preferred_day: updatedDays.join(", ")
                            }));
                          }}
                          className="text-blue-600 dark:text-sky-400"
                        />
                        {day}
                      </label>
                    ))}
                  </div>
                </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1">
                  Preferred Time for Meetings
                </label>
                <input
                  type="text"
                  value={reviewFormData.preferred_time}
                  onChange={(e) =>
                    setReviewFormData(prev => ({ ...prev, preferred_time: e.target.value }))
                  }
                  placeholder="e.g., 6 PM - 8 PM"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200 placeholder-slate-400 dark:placeholder-gray-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={submittingReview}
                className="bg-blue-600 hover:bg-blue-700 dark:bg-sky-400 dark:hover:bg-sky-500 text-white px-4 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submittingReview ? 'Saving...' : existingReview ? 'Save Changes' : 'Submit Review'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

export default StudyingDashboard
