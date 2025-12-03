import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { collegeService, counsellingService } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import type { Branch } from '../types'

const CollegeDetailPage = () => {
  const { collegeId } = useParams<{ collegeId: string }>()
  const { user } = useAuth()
  const [college, setCollege] = useState<any>(null)

  useEffect(() => {
    if (collegeId) {
      loadCollege()
    }
  }, [collegeId])

  const loadCollege = async () => {
    try {
      const data = await collegeService.detail(collegeId!)
      setCollege(data)
    } catch (err) {
      console.error('Error loading college:', err)
    }
  }

  const addToChoices = async (uniqueKey: string) => {
    try {
      // place at end of list
      const choices = await (await import('../services/api')).counsellingService.choices.list()
      const nextOrder = choices.length > 0 ? Math.max(...choices.map(c => c.order_of_list)) + 1 : 1
      await counsellingService.choices.create(uniqueKey, nextOrder)
      alert('Added to your choices!')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error adding choice')
    }
  }

  if (!college) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-3xl font-bold mb-2">{college.college_name}</h1>
        <p className="text-gray-600">Code: {college.college_code} | Location: {college.location}</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Branches</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Branch</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cluster</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {college.branches?.map((branch: Branch) => (
                <tr key={branch.unique_key} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link
                      to={`/branches/${branch.unique_key}`}
                      className="text-primary-600 hover:underline"
                    >
                      {branch.branch_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{branch.cluster.cluster_name}</td>
                  <td className="px-4 py-3">
                    {user?.type_of_student === 'counselling' && (
                      <button
                        onClick={() => addToChoices(branch.unique_key)}
                        className="text-primary-600 hover:text-primary-800 text-sm"
                      >
                        Add to Choices
                      </button>
                    )}
                    <Link
                      to={`/branches/${branch.unique_key}`}
                      className="ml-4 text-sm text-gray-700 hover:underline"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default CollegeDetailPage
