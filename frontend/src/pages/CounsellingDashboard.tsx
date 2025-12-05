import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { counsellingService, categoryService } from '../services/api'
import type { Recommendation, CounsellingChoice, Category } from '../types'

const CounsellingDashboard = () => {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [choices, setChoices] = useState<CounsellingChoice[]>([])
  const [loading, setLoading] = useState(false)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [category, setCategory] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [year, setYear] = useState('2025')
  const [round, setRound] = useState('r1')
  const [draggedChoice, setDraggedChoice] = useState<number | null>(null)


  
  // compute the best display name once
  const displayName = useMemo(() => {
  // 1) if backend sent a name, show first name
  const full = user?.name?.trim();
  if (full) return full.split(' ')[0];

  // 2) else derive from email (before @), clean dots/underscores/digits
  const username = (user?.email_id || '').split('@')[0] || '';
  // take first token before ., _, or -
  const token = username.split(/[._-]/)[0] || username;
  // strip digits like is23 -> is
  const noDigits = token.replace(/\d+/g, '');
  // capitalize first letter
  if (!noDigits) return 'User';
  return noDigits.charAt(0).toUpperCase() + noDigits.slice(1);
}, [user]);


  useEffect(() => {
    loadChoices()
    loadCategories()
    if (user?.category) setCategory(user.category)
  }, [user])

  const loadChoices = async () => {
    try {
      const data = await counsellingService.choices.list()
      setChoices(data.sort((a, b) => a.order_of_list - b.order_of_list))
    } catch (err) {
      console.error('Error loading choices:', err)
    }
  }

  const loadCategories = async () => {
    try {
      const data = await categoryService.list()
      setCategories(data)
    } catch (err) {
      console.error('Error loading categories:', err)
    }
  }

  const handleReorder = async (choiceId: number, newOrder: number) => {
    try {
      await counsellingService.choices.update(choiceId, newOrder)
      await loadChoices()
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error reordering choice')
    }
  }

  // Replace this function only
const moveChoice = async (index: number, direction: 'up' | 'down') => {
  if (direction === 'up' && index === 0) return
  if (direction === 'down' && index === choices.length - 1) return

  const neighborIndex = direction === 'up' ? index - 1 : index + 1
  const current = choices[index]
  const neighbor = choices[neighborIndex]

  // Optimistic UI swap (so it feels instant)
  const prev = choices
  const next = [...choices]
  next[index] = neighbor
  next[neighborIndex] = current
  setChoices(next)

  try {
    // Do a true swap on the server, sequentially, to avoid "already taken"
    await counsellingService.choices.update(current.choice_id, neighbor.order_of_list)
    await counsellingService.choices.update(neighbor.choice_id, current.order_of_list)

    // Refresh to sync with server truth
    await loadChoices()
  } catch (err: any) {
    // Revert UI on error
    setChoices(prev)
    alert(err.response?.data?.error || 'Error reordering choice')
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
      const nextOrder =
        choices.length > 0 ? Math.max(...choices.map(c => c.order_of_list)) + 1 : 1
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
    } catch {
      alert('Error removing choice')
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Counselling Dashboard</h1>
        <p className="mt-2 text-gray-600">
          <p className="mt-2 text-gray-600">
  Welcome, {displayName}.{' '}
  Your KCET Rank: <strong>{user?.kcet_rank || 'Not set'}</strong>
</p>


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
          <h2 className="text-xl font-semibold mb-4">
            My Saved Choices ({choices.length})
          </h2>
          {choices.length === 0 ? (
            <p className="text-gray-500">No choices saved yet</p>
          ) : (
            <div className="space-y-2">
              {choices.map((choice, index) => (
                <div
                  key={choice.choice_id}
                  className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  draggable
                  onDragStart={() => setDraggedChoice(choice.choice_id)}
                  onDragOver={e => e.preventDefault()}
                  onDrop={e => {
                    e.preventDefault()
                    if (draggedChoice && draggedChoice !== choice.choice_id) {
                      handleReorder(draggedChoice, choice.order_of_list)
                    }
                    setDraggedChoice(null)
                  }}
                >
                  <div className="flex items-center space-x-2">
                    <div className="flex flex-col">
                      <button
                        onClick={() => moveChoice(index, 'up')}
                        disabled={index === 0}
                        className="text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ↑
                      </button>
                      <button
                        onClick={() => moveChoice(index, 'down')}
                        disabled={index === choices.length - 1}
                        className="text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ↓
                      </button>
                    </div>
                    <div>
                      <span className="font-semibold">{choice.order_of_list}.</span>{' '}
                      {choice.unique_key_data?.college.college_name} -{' '}
                      {choice.unique_key_data?.branch_name}
                    </div>
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
              onChange={e => setCategory(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.category} value={cat.category}>
                  {cat.category} ({cat.fall_back})
                </option>
              ))}
            </select>
            <select
              value={year}
              onChange={e => setYear(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
            </select>
            <select
              value={round}
              onChange={e => setRound(e.target.value)}
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      College
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Branch
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Opening Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Closing Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Distance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recommendations.map(rec => (
                    <tr key={rec.unique_key} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          to={`/colleges/${rec.college.college_id}`}
                          className="text-primary-600 hover:underline"
                        >
                          {rec.college.college_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {rec.branch.branch_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.opening_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{rec.closing_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {rec.distance_from_rank}
                      </td>
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
