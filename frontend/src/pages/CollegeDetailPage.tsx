import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { collegeService, branchService, reviewService, counsellingService, meetingService, categoryService } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import StarRating from '../components/StarRating'
import type { Branch, Category, Review } from '../types'

const CollegeDetailPage = () => {
  const { collegeId } = useParams<{ collegeId: string }>()
  const { user } = useAuth()
  const [college, setCollege] = useState<any>(null)
  const [cutoffData, setCutoffData] = useState<any>({})
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null)
  const [branchCutoff, setBranchCutoff] = useState<any>(null)
  const [reviews, setReviews] = useState<any>(null)
  const [students, setStudents] = useState<any[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [categories, setCategories] = useState<Category[]>([])

  useEffect(() => {
    if (collegeId) {
      loadCollege()
      loadCutoffData()
      loadReviews()
      loadCategories()
    }
  }, [collegeId])

  useEffect(() => {
    // Set default category from user
    if (user?.category && !selectedCategory) {
      setSelectedCategory(user.category)
    }
  }, [user])

  useEffect(() => {
    if (selectedBranch && selectedCategory) {
      loadBranchCutoff()
    }
  }, [selectedBranch, selectedCategory])

  useEffect(() => {
    if (selectedBranch) {
      loadBranchCutoff()
      loadBranchReviews()
      if (user?.type_of_student === 'counselling') {
        loadBranchStudents()
      }
    }
  }, [selectedBranch])

  const loadCollege = async () => {
    try {
      const data = await collegeService.detail(collegeId!)
      setCollege(data)
    } catch (err) {
      console.error('Error loading college:', err)
    }
  }

  const loadCutoffData = async () => {
    try {
      const data = await collegeService.cutoff(collegeId!)
      setCutoffData(data)
    } catch (err) {
      console.error('Error loading cutoff:', err)
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

  const loadBranchCutoff = async () => {
    try {
      const data = await branchService.cutoff(selectedBranch!, selectedCategory || undefined)
      setBranchCutoff(data)
    } catch (err) {
      console.error('Error loading branch cutoff:', err)
    }
  }

  const loadReviews = async () => {
    try {
      const data = await reviewService.collegeReviews(collegeId!)
      setReviews(data)
    } catch (err) {
      console.error('Error loading reviews:', err)
    }
  }

  const loadBranchReviews = async () => {
    try {
      const data = await reviewService.branchReviews(selectedBranch!)
      setReviews(data)
    } catch (err) {
      console.error('Error loading branch reviews:', err)
    }
  }

  const loadBranchStudents = async () => {
    try {
      const data = await meetingService.branchStudents(selectedBranch!)
      setStudents(data.students || [])
    } catch (err) {
      console.error('Error loading students:', err)
    }
  }

  const addToChoices = async (uniqueKey: string) => {
    try {
      const choices = await counsellingService.choices.list()
      const nextOrder = choices.length > 0 ? Math.max(...choices.map(c => c.order_of_list)) + 1 : 1
      await counsellingService.choices.create(uniqueKey, nextOrder)
      alert('Added to your choices!')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error adding choice')
    }
  }

  const prepareChartData = (categoryData: any) => {
    if (!categoryData) return []
    return [
      { year: '2022', R1: parseInt(categoryData['2022']?.r1) || 0, R2: parseInt(categoryData['2022']?.r2) || 0, R3: parseInt(categoryData['2022']?.r3) || 0 },
      { year: '2023', R1: parseInt(categoryData['2023']?.r1) || 0, R2: parseInt(categoryData['2023']?.r2) || 0, R3: parseInt(categoryData['2023']?.r3) || 0 },
      { year: '2024', R1: parseInt(categoryData['2024']?.r1) || 0, R2: parseInt(categoryData['2024']?.r2) || 0, R3: parseInt(categoryData['2024']?.r3) || 0 },
      { year: '2025', R1: parseInt(categoryData['2025']?.r1) || 0, R2: parseInt(categoryData['2025']?.r2) || 0, R3: parseInt(categoryData['2025']?.r3) || 0 },
    ].filter(row => row.R1 > 0 || row.R2 > 0 || row.R3 > 0)
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

      <div className="grid md:grid-cols-2 gap-6">
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
                      <button
                        onClick={() => setSelectedBranch(branch.unique_key)}
                        className="text-primary-600 hover:underline"
                      >
                        {branch.branch_name}
                      </button>
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
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedBranch && branchCutoff && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Cutoff Trends</h2>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="border rounded px-3 py-1"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.category} value={cat.category}>
                    {cat.category} ({cat.fall_back})
                  </option>
                ))}
              </select>
            </div>
            {Object.keys(branchCutoff.categories || {}).map(category => {
              const chartData = prepareChartData(branchCutoff.categories[category])
              if (chartData.length === 0) return null
              return (
                <div key={category} className="mb-6">
                  <h3 className="font-medium mb-2">Category: {category}</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="R1" stroke="#8884d8" name="Round 1" />
                      <Line type="monotone" dataKey="R2" stroke="#82ca9d" name="Round 2" />
                      <Line type="monotone" dataKey="R3" stroke="#ffc658" name="Round 3" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {reviews && (
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-xl font-semibold mb-4">Reviews & Ratings</h2>
          
          {/* Overall Average Ratings */}
          {reviews.average_ratings && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Overall Average Ratings</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(reviews.average_ratings).map(([key, value]: [string, any]) => (
                  <div key={key} className="text-center">
                    <div className="flex justify-center mb-1">
                      <StarRating rating={Math.round(value || 0)} readonly size="sm" />
                    </div>
                    <div className="text-sm font-semibold text-primary-600">
                      {value ? value.toFixed(1) : 'N/A'}
                    </div>
                    <div className="text-xs text-gray-600">{key.replace('avg_', '').replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Individual Reviews Table */}
          {reviews.reviews && reviews.reviews.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Individual Reviews ({reviews.total_reviews || 0})</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewer</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attribute</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Review</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {reviews.reviews.map((review: Review) => {
                      const ratingFields = [
                        { key: 'teaching', label: 'Teaching Quality', rating: review.teaching_rating, review: review.teaching_review },
                        { key: 'courses', label: 'Course Curriculum', rating: review.courses_rating, review: review.courses_review },
                        { key: 'library', label: 'Library Facilities', rating: review.library_rating, review: review.library_review },
                        { key: 'research', label: 'Research Opportunities', rating: review.research_rating, review: review.research_review },
                        { key: 'internship', label: 'Internship Support', rating: review.internship_rating, review: review.internship_review },
                        { key: 'infrastructure', label: 'Infrastructure', rating: review.infrastructure_rating, review: review.infrastructure_review },
                        { key: 'administration', label: 'Administration', rating: review.administration_rating, review: review.administration_review },
                        { key: 'extracurricular', label: 'Extracurricular Activities', rating: review.extracurricular_rating, review: review.extracurricular_review },
                        { key: 'safety', label: 'Safety & Security', rating: review.safety_rating, review: review.safety_review },
                        { key: 'placement', label: 'Placement Support', rating: review.placement_rating, review: review.placement_review },
                      ]
                      return ratingFields.map((field, idx) => (
                        <tr key={`${review.review_id}-${field.key}`} className="hover:bg-gray-50">
                          {idx === 0 && (
                            <td rowSpan={10} className="px-4 py-4 whitespace-nowrap align-top">
                              <div className="font-medium text-gray-900">
                                {review.student_user_id_data?.name || review.student_user_id_data?.email_id || review.student_user_id}
                              </div>
                            </td>
                          )}
                          <td className="px-4 py-4 whitespace-nowrap">{field.label}</td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <StarRating rating={field.rating} readonly size="sm" />
                          </td>
                          <td className="px-4 py-4">{field.review || '-'}</td>
                        </tr>
                      ))
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {user?.type_of_student === 'counselling' && selectedBranch && students.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-xl font-semibold mb-4">Students from this Branch</h2>
          <div className="space-y-2">
            {students.map(student => (
              <div key={student.student_user_id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span>Student ID: {student.student_user_id} (Started: {student.year_of_starting})</span>
                <Link
                  to="/meetings"
                  className="text-primary-600 hover:text-primary-800 text-sm"
                >
                  Request Meeting
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CollegeDetailPage

