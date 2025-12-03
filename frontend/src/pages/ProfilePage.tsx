import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authService, categoryService } from '../services/api'
import type { Category } from '../types'

const ProfilePage = () => {
  const { user } = useAuth()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [categories, setCategories] = useState<Category[]>([])
  const [formData, setFormData] = useState({
    name: user?.name || '',
    category: user?.category || '',
    email_id: user?.email_id || '',
    phone_number: user?.phone_number || '',
    kcet_rank: user?.kcet_rank?.toString() || '',
  })

  // If user loads after first render, sync form once it’s available
  useEffect(() => {
    if (!user) return
    setFormData({
      name: user.name || '',
      category: user.category || '',
      email_id: user.email_id || '',
      phone_number: user.phone_number || '',
      kcet_rank: user.kcet_rank != null ? String(user.kcet_rank) : '',
    })
  }, [user])

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await categoryService.list() // /api/colleges/categories/
        setCategories(Array.isArray(data) ? data : [])
      } catch (err) {
        console.error('Error loading categories:', err)
        setCategories([])
      }
    }
    loadCategories()
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const updateData: any = {
        name: formData.name,
        category: formData.category || null,
      }

      if (user?.type_of_student === 'counselling') {
        updateData.kcet_rank =
          formData.kcet_rank !== '' && formData.kcet_rank != null
            ? parseInt(formData.kcet_rank, 10)
            : null
      }

      const updatedUser = await authService.updateProfile(updateData)

      // Keep localStorage user fresh so Navbar / other places see it
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        const userData = JSON.parse(storedUser)
        const newUserData = { ...userData, ...updatedUser }
        localStorage.setItem('user', JSON.stringify(newUserData))
      }

      setSuccess('Profile updated successfully!')
      // Reload to refresh AuthContext from localStorage
      setTimeout(() => window.location.reload(), 800)
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Error updating profile')
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold mb-6">Edit Profile</h1>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Category</option>
              {categories.map(cat => (
                <option key={cat.category} value={cat.category}>
                  {cat.category} ({cat.fall_back})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={formData.email_id}
              disabled
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100"
            />
            <p className="mt-1 text-sm text-gray-500">Email cannot be changed</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Phone Number</label>
            <input
              type="tel"
              value={formData.phone_number}
              disabled
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100"
            />
            <p className="mt-1 text-sm text-gray-500">Phone number cannot be changed</p>
          </div>

          {user.type_of_student === 'counselling' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">KCET Rank</label>
              <input
                type="number"
                name="kcet_rank"
                value={formData.kcet_rank}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProfilePage
