import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { counsellingService, collegeService } from '../services/api'
import type { Recommendation, CounsellingChoice } from '../types'

const CounsellingDashboard = () => {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [choices, setChoices] = useState<CounsellingChoice[]>([])
  const [loading, setLoading] = useState(false)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [category, setCategory] = useState('')
  const [year, setYear] = useState('2025')
  const [round, setRound] = useState('r1')

  useEffect(() => {
    loadChoices()
  }, [])

  const loadChoices = async () => {
    try {
      const data = await counsellingService.choices.list()
      setChoices(data.sort((a, b) => a.order_of_list - b.order_of_list))
    } catch (err) {
      console.error('Error loading choices:', err)
    }
  }

  const loadRecommendations = async () => {
    if (!user?.kcet_rank) {
      alert('Please set your KCET rank first')
      return
    }

    setLoading(true)
    try {
      const data = await counsellingService.recommendations(
        user.kcet_rank,
        category || undefined,
        year,
        round
      )
      setRecommendations(data.recommendations)
      setShowRecommendations(true)
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error loading recommendations')
    } finally {
      setLoading(false)
    }
  }

  const addToChoices = async (uniqueKey: string) => {
    try {
      const nextOrder = choices.length > 0 ? Math.max(...choices.map(c => c.order_of_list)) + 1 : 1
      await counsellingService.choices.create(uniqueKey, nextOrder)
      await loadChoices()
      alert('Added to your choices!')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error adding choice')
    }
  }

  const removeChoice = async (choiceId: number) => {
    if (!confirm('Remove this choice?')) return
    try {
      await counsellingService.choices.delete(choiceId)
      await loadChoices()
    } catch (err) {
      alert('Error removing choice')
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Counselling Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome, {user?.email_id}. Your KCET Rank: <strong>{user?.kcet_rank || 'Not set'}</strong>
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button
              onClick={loadRecommendations}
              disabled={loading}
              className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'View Recommendations'}
            </button>
            <Link
              to="/search"
              className="block w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-center"
            >
              Search Colleges
            </Link>
            <Link
              to="/meetings"
              className="block w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-center"
            >
              Meet Seniors
            </Link>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">My Saved Choices ({choices.length})</h2>
          {choices.length === 0 ? (
            <p className="text-gray-500">No choices saved yet</p>
          ) : (
            <div className="space-y-2">
              {choices.map(choice => (
                <div key={choice.choice_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div>
                    <span className="font-semibold">{choice.order_of_list}.</span>{' '}
                    {choice.unique_key_data?.college.college_name} - {choice.unique_key_data?.branch_name}
                  </div>
                  <button
                    onClick={() => removeChoice(choice.choice_id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showRecommendations && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="mb-4 flex flex-wrap gap-4 items-center">
            <h2 className="text-xl font-semibold">Recommendations</h2>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="">All Categories</option>
              <option value="GM">GM</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="OBC">OBC</option>
            </select>
            <select
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
            </select>
            <select
              value={round}
              onChange={(e) => setRound(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="r1">Round 1</option>
              <option value="r2">Round 2</option>
              <option value="r3">Round 3</option>
            </select>
            <button
              onClick={loadRecommendations}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
            >
              Refresh
            </button>
          </div>

          {recommendations.length === 0 ? (
            <p className="text-gray-500">No recommendations found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">College</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Branch</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Opening Rank</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Closing Rank</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Distance</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recommendations.map((rec) => (
                    <tr key={rec.unique_key} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          to={`/colleges/${rec.college.college_id}`}
                          className="text-primary-600 hover:underline"
                        >
                          {rec.college.college_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.branch.branch_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.opening_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.closing_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.distance_from_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => addToChoices(rec.unique_key)}
                          className="text-primary-600 hover:text-primary-800"
                        >
                          Add to Choices
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CounsellingDashboard

