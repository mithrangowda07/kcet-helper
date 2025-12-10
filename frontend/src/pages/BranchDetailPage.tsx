import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { branchService, reviewService, meetingService } from '../services/api'
import StarRating from '../components/StarRating'
import CustomTooltip from '../components/charts/CustomTooltip';
import type { Branch, Review } from '../types'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

type BranchCutoffResponse = {
  categories?: Record<
    string,
    Record<string, { r1?: number | string; r2?: number | string; r3?: number | string }>
  >
}

// Fallback chains
const FALLBACK_ORDER: Record<string, string[]> = {
  "1R": ["1R", "1G", "GM"],
  "1K": ["1K", "1G", "GM"],
  "1G": ["1G", "GM"],

  "2AR": ["2AR", "2AG", "GM"],
  "2AK": ["2AK", "2AG", "GM"],
  "2AG": ["2AG", "GM"],
  "2BR": ["2BR", "2BG", "GM"],
  "2BK": ["2BK", "2BG", "GM"],
  "2BG": ["2BG", "GM"],

  "3AK": ["3AK", "3AG", "GM"],
  "3AR": ["3AR", "3AG", "GM"],
  "3AG": ["3AG", "GM"],
  "3BK": ["3BK", "3BG", "GM"],
  "3BR": ["3BR", "3BG", "GM"],
  "3BG": ["3BG", "GM"],

  "STK": ["STK", "STG", "GM"],
  "STR": ["STR", "STG", "GM"],
  "STG": ["STG", "GM"],

  "SCK": ["SCK", "SCG", "GM"],
  "SCR": ["SCR", "SCG", "GM"],
  "SCG": ["SCG", "GM"],

  "GMR": ["GMR", "GM"],
  "GMK": ["GMK", "GM"],

  "GM": ["GM"]
}

const BranchDetailPage = () => {
  const { uniqueKey } = useParams<{ uniqueKey: string }>()
  const { user } = useAuth()
  const [branch, setBranch] = useState<Branch | null>(null)
  const [cutoff, setCutoff] = useState<BranchCutoffResponse | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [reviews, setReviews] = useState<{
    reviews: Review[]
    average_ratings: Record<string, number>
    total_reviews: number
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [requestingMeeting, setRequestingMeeting] = useState<string | null>(null)

  const prepareChartData = (
    categoryData?: Record<string, { r1?: any; r2?: any; r3?: any }>
  ) => {
    if (!categoryData) return []
    const years = ['2022', '2023', '2024', '2025']
    return years
      .map(y => ({
        year: y,
        R1: Number(categoryData[y]?.r1 ?? 0),
        R2: Number(categoryData[y]?.r2 ?? 0),
        R3: Number(categoryData[y]?.r3 ?? 0),
      }))
      .filter(row => row.R1 || row.R2 || row.R3)
  }

  const categories = useMemo(
    () => Object.keys(cutoff?.categories || {}),
    [cutoff]
  )

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        if (!uniqueKey) return

        const branchData = await branchService.detail(uniqueKey)
        setBranch(branchData)

        const cutoffData = await branchService.cutoff(uniqueKey)
        setCutoff(cutoffData)

        const reviewData = await reviewService.branchReviews(uniqueKey)
        setReviews(reviewData)

        // Set default category to user's category if logged in
        if (user?.category && !selectedCategory) {
          setSelectedCategory(user.category)
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [uniqueKey, user?.category])

  const requestMeeting = async (studyingUserId?: string) => {
    if (!studyingUserId) {
      alert('Unable to request meeting for this reviewer.')
      return
    }
    setRequestingMeeting(studyingUserId)
    try {
      await meetingService.request(studyingUserId)
      alert('Meeting request sent. Track it on the Meetings page.')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error sending meeting request')
    } finally {
      setRequestingMeeting(null)
    }
  }

  if (loading) return <div className="p-8 text-slate-600 dark:text-gray-400">Loading…</div>
  if (!branch) return <div className="p-8 text-slate-600 dark:text-gray-400">Branch not found.</div>

  // BUILD CHART LIST
  // If user is logged in and has a category, default to showing that category
  // but still allow changing via the dropdown
  let chartCategories: string[] = []

  if (!selectedCategory) {
    // If user is logged in and has category, use it; otherwise show all
    if (user?.category) {
      const chain = FALLBACK_ORDER[user.category] || [user.category, "GM"]
      const seen = new Set<string>()
      chartCategories = chain.filter(c => {
        if (seen.has(c)) return false
        seen.add(c)
        return cutoff?.categories?.[c]
      })
      // If no categories found for user's category, show all
      if (chartCategories.length === 0) {
        chartCategories = categories
      }
    } else {
      chartCategories = categories
    }
  } else {
    const chain = FALLBACK_ORDER[selectedCategory] || [selectedCategory, "GM"]
    const seen = new Set<string>()
    chartCategories = chain.filter(c => {
      if (seen.has(c)) return false
      seen.add(c)
      return cutoff?.categories?.[c]
    })
  }

  // Review attribute columns
  const FIELDS = [
    { key: 'teaching_review', label: 'Teaching' },
    { key: 'courses_review', label: 'Courses' },
    { key: 'library_review', label: 'Library' },
    { key: 'research_review', label: 'Research' },
    { key: 'internship_review', label: 'Internship' },
    { key: 'infrastructure_review', label: 'Infrastructure' },
    { key: 'administration_review', label: 'Administration' },
    { key: 'extracurricular_review', label: 'Extracurricular' },
    { key: 'safety_review', label: 'Safety' },
    { key: 'placement_review', label: 'Placement' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <Link to={`/colleges/${branch.college.college_id}`} className="text-blue-600 dark:text-sky-400 hover:underline">
        ← Back to {branch.college.college_name}
      </Link>

      <h1 className="text-3xl font-bold mt-4 text-slate-800 dark:text-gray-100">{branch.branch_name}</h1>
      <p className="text-slate-600 dark:text-gray-400 mb-6">
        College: <strong>{branch.college.college_name}</strong> • Cluster: {branch.cluster.cluster_name}
      </p>

      {/* Cutoff */}
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-8 border border-slate-300 dark:border-slate-700">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-slate-800 dark:text-gray-100">Cutoff Trends</h2>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="border border-slate-300 dark:border-slate-600 rounded px-3 py-1 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {chartCategories.map(cat => {
            const data = prepareChartData(cutoff?.categories?.[cat])
            if (!data.length) return null

            return (
              <div
                key={cat}
                className="rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-slate-900 dark:text-gray-100">Category: {cat}</h3>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-50 dark:bg-sky-900/30 text-blue-700 dark:text-sky-300 border border-blue-100 dark:border-sky-800">
                    2022-25 • R1-R3
                  </span>
                </div>
                <ResponsiveContainer width="100%" height={230}>
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line type="monotone" dataKey="R1" stroke="#16a34a" strokeWidth={2}/>
                    <Line type="monotone" dataKey="R2" stroke="#2563eb" strokeWidth={2}/>
                    <Line type="monotone" dataKey="R3" stroke="#dc2626" strokeWidth={2}/>
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )
          })}
        </div>

      </div>
      {/* Average Ratings */}
      {reviews?.average_ratings && (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-6 border border-slate-300 dark:border-slate-700">
          <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-gray-100">Overall Average Ratings</h2>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(reviews.average_ratings).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="flex justify-center mb-1">
                  <StarRating rating={Math.round(value || 0)} readonly size="sm" />
                </div>
                <div className="text-sm font-semibold text-blue-600 dark:text-sky-400">
                  {value?.toFixed?.(1) || "N/A"}
                </div>
                <div className="text-xs text-slate-600 dark:text-gray-400">
                  {key.replace("avg_", "").replace("_", " ")}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reviews Table */}
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 border border-slate-300 dark:border-slate-700">
        <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-gray-100">Reviews (By Students)</h2>

        {reviews?.reviews?.length ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
              <thead className="bg-slate-50 dark:bg-slate-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase w-48">
                    Reviewer
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                    Preferred Day
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                    Preferred Time
                  </th>
                  {FIELDS.map(f => (
                    <th key={f.key} className="px-6 py-4 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase min-w-[200px]">
                      {f.label}
                    </th>
                  ))}
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                    Meeting
                  </th>
                </tr>
              </thead>

              <tbody>
                {reviews.reviews.map(r => (
                  <tr key={r.review_id} className="hover:bg-slate-50 dark:hover:bg-slate-700">
                    <td className="px-6 py-4 align-top font-medium text-sm text-slate-900 dark:text-gray-100">
                      {r.student_user_id_data?.name ||
                       r.student_user_id_data?.email_id ||
                       r.student_user_id}
                    </td>

                    <td className="px-6 py-4 align-top text-sm text-slate-800 dark:text-gray-200">
                      {r.preferred_day?.trim() || '—'}
                    </td>
                    <td className="px-6 py-4 align-top text-sm text-slate-800 dark:text-gray-200">
                      {r.preferred_time?.trim() || '—'}
                    </td>

                    {FIELDS.map(f => (
                      <td key={f.key} className="px-6 py-4 align-top text-sm text-left text-slate-900 dark:text-gray-100">
                        <div className="whitespace-normal break-words">
                          {(r as any)[f.key]?.trim() || "—"}
                        </div>
                      </td>
                    ))}
                    <td className="px-6 py-4 align-top text-sm">
                      {user?.type_of_student === 'counselling' ? (
                        <button
                          onClick={() => requestMeeting(r.student_user_id_data?.student_user_id)}
                          disabled={!r.student_user_id_data?.student_user_id || requestingMeeting === r.student_user_id_data?.student_user_id}
                          className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300 disabled:text-slate-400 dark:disabled:text-gray-600 disabled:cursor-not-allowed"
                        >
                          {requestingMeeting === r.student_user_id_data?.student_user_id ? 'Requesting...' : 'Request Meeting'}
                        </button>
                      ) : (
                        <span className="text-slate-400 dark:text-gray-500 text-xs">Counselling students only</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        ) : (
          <p className="text-slate-500 dark:text-gray-400">No reviews yet for this branch.</p>
        )}
      </div>
    </div>
  )
}

export default BranchDetailPage
