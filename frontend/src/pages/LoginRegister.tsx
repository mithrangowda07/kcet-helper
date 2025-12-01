import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { branchService } from '../services/api'
import type { Branch } from '../types'

const LoginRegister = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [studentType, setStudentType] = useState<'counselling' | 'studying'>('counselling')
  const [formData, setFormData] = useState({
    email_id: '',
    phone_number: '',
    password: '',
    password_confirm: '',
    kcet_rank: '',
    college_code: '',
    unique_key: '',
    year_of_starting: '',
  })
  const [branches, setBranches] = useState<Branch[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  const handleCollegeCodeChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const collegeCode = e.target.value.trim()
    setFormData(prev => ({ ...prev, college_code: collegeCode }))
    setError('')
    
    if (collegeCode.length < 2) {
      setBranches([])
      setFormData(prev => ({ ...prev, unique_key: '' }))
      return
    }

    try {
      const branchList = await branchService.byCollegeCode(collegeCode)
      setBranches(branchList)
      setFormData(prev => ({
        ...prev,
        unique_key: branchList.some(branch => branch.unique_key === prev.unique_key)
          ? prev.unique_key
          : ''
      }))
    } catch (err) {
      console.error('Error fetching branches:', err)
      setBranches([])
      setFormData(prev => ({ ...prev, unique_key: '' }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(formData.email_id, formData.password)
        navigate('/dashboard/counselling')
      } else {
        const registerData: any = {
          type_of_student: studentType,
          email_id: formData.email_id,
          phone_number: formData.phone_number,
          password: formData.password,
          password_confirm: formData.password_confirm,
        }

        if (studentType === 'counselling') {
          registerData.kcet_rank = formData.kcet_rank ? parseInt(formData.kcet_rank) : null
        } else {
          registerData.college_code = formData.college_code
          registerData.unique_key = formData.unique_key || null
          registerData.year_of_starting = formData.year_of_starting ? parseInt(formData.year_of_starting) : null
        }

        await register(registerData)
        navigate(studentType === 'counselling' ? '/dashboard/counselling' : '/dashboard/studying')
      }
    } catch (err: any) {
      // Handle detailed validation errors
      if (err.response?.data?.errors) {
        const errors = err.response.data.errors
        const errorMessages = Object.entries(errors)
          .map(([field, messages]: [string, any]) => {
            const msg = Array.isArray(messages) ? messages.join(', ') : messages
            return `${field}: ${msg}`
          })
          .join('\n')
        setError(errorMessages || err.response.data.message || 'Validation failed')
      } else {
        setError(err.response?.data?.error || err.response?.data?.message || err.message || 'An error occurred')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            {isLogin ? 'Sign in to your account' : 'Create a new account'}
          </h2>
        </div>

        {!isLogin && (
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setStudentType('counselling')}
              className={`flex-1 py-2 px-4 rounded-md ${
                studentType === 'counselling'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Counselling Student
            </button>
            <button
              type="button"
              onClick={() => setStudentType('studying')}
              className={`flex-1 py-2 px-4 rounded-md ${
                studentType === 'studying'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Studying Student
            </button>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded whitespace-pre-line">
            <strong>Error:</strong>
            <div className="mt-1">{error}</div>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  name="email_id"
                  required
                  value={formData.email_id}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                <input
                  type="tel"
                  name="phone_number"
                  required
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </>
          )}

          {isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                name="email_id"
                required
                value={formData.email_id}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <div className="mt-1 relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                className="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                {showPassword ? (
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
                <div className="mt-1 relative">
                  <input
                    type={showPasswordConfirm ? "text" : "password"}
                    name="password_confirm"
                    required
                    value={formData.password_confirm}
                    onChange={handleInputChange}
                    className="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswordConfirm ? (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {studentType === 'counselling' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">KCET Rank</label>
                  <input
                    type="number"
                    name="kcet_rank"
                    required
                    value={formData.kcet_rank}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              )}

              {studentType === 'studying' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">College Code</label>
                    <input
                      type="text"
                      name="college_code"
                      required
                      value={formData.college_code}
                      onChange={handleCollegeCodeChange}
                      placeholder="e.g., E001"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Branch</label>
                    <select
                      name="unique_key"
                      required
                      value={formData.unique_key}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="">Select a branch</option>
                      {branches.map(branch => (
                        <option key={branch.unique_key} value={branch.unique_key}>
                          {branch.branch_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Year of Starting</label>
                    <input
                      type="number"
                      name="year_of_starting"
                      required
                      value={formData.year_of_starting}
                      onChange={handleInputChange}
                      min="2020"
                      max={new Date().getFullYear()}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </>
              )}
            </>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {loading ? 'Processing...' : isLogin ? 'Sign in' : 'Register'}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
                setFormData({
                  email_id: '',
                  phone_number: '',
                  password: '',
                  password_confirm: '',
                  kcet_rank: '',
                  college_code: '',
                  unique_key: '',
                  year_of_starting: '',
                })
              }}
              className="text-primary-600 hover:text-primary-500"
            >
              {isLogin ? "Don't have an account? Register" : 'Already have an account? Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginRegister

