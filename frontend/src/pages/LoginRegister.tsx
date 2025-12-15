import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { branchService, collegeService, categoryService } from '../services/api'
import type { Branch, College, Category } from '../types'

const LoginRegister = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [studentType, setStudentType] = useState<'counselling' | 'studying'>('counselling')
  const { user, login, register } = useAuth()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: '',
    email_id: '',
    phone_number: '',
    password: '',
    password_confirm: '',
    category: '',
    kcet_rank: '',
    college_code: '',
    unique_key: '',
    year_of_starting: '',
  })

  const [branches, setBranches] = useState<Branch[]>([])
  const [colleges, setColleges] = useState<College[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  // College change handler (for <select>)
  const handleCollegeCodeChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const collegeCode = e.target.value
    setFormData(prev => ({ ...prev, college_code: collegeCode }))
    setError('')

    if (!collegeCode) {
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

  // Load colleges when Studying form is visible (and also if returning to this tab)
  useEffect(() => {
    if (!isLogin && studentType === 'studying') {
      collegeService
        .list()
        .then(setColleges)
        .catch(() => setColleges([]))
    }
  }, [isLogin, studentType])

  // Load categories when registration view is open (for both student types)
  useEffect(() => {
    if (!isLogin) {
      categoryService
        .list()
        .then((data) => {
          setCategories(Array.isArray(data) ? data : [])
        })
        .catch(async (err) => {
          console.error('Error loading categories, using fallback:', err)
          // Fallback to hardcoded categories
          try {
            const { HARDCODED_CATEGORIES } = await import('../data/categories')
            setCategories(HARDCODED_CATEGORIES)
          } catch {
            setCategories([])
          }
        })
    }
  }, [isLogin])

  // If a college is already selected (e.g., user toggled tabs), ensure branches are loaded
  useEffect(() => {
    if (!isLogin && studentType === 'studying' && formData.college_code) {
      branchService
        .byCollegeCode(formData.college_code)
        .then(setBranches)
        .catch(() => setBranches([]))
    } else if (studentType !== 'studying') {
      setBranches([])
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLogin, studentType])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(formData.email_id, formData.password)
        navigate(user?.type_of_student === 'counselling' ? '/dashboard/counselling' : '/dashboard/studying')
      } else {
        const registerData: any = {
          type_of_student: studentType,
          name: formData.name,
          email_id: formData.email_id,
          phone_number: formData.phone_number,
          password: formData.password,
          password_confirm: formData.password_confirm,
        }

        if (studentType === 'counselling') {
          registerData.kcet_rank = formData.kcet_rank ? parseInt(formData.kcet_rank) : null
          registerData.category = formData.category || null
        } else {
          registerData.college_code = formData.college_code
          registerData.unique_key = formData.unique_key || null
          registerData.year_of_starting = formData.year_of_starting ? parseInt(formData.year_of_starting) : null
          registerData.category = formData.category || null
        }

        await register(registerData)
        // After successful registration, switch to login view instead of auto-login
        setIsLogin(true)
        setError('') // clear any previous errors
        setFormData({
          name: '',
          email_id: '',
          phone_number: '',
          password: '',
          password_confirm: '',
          category: '',
          kcet_rank: '',
          college_code: '',
          unique_key: '',
          year_of_starting: '',
        })
      }
    } catch (err: any) {
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
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#111827] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white dark:bg-slate-800 p-8 rounded-lg shadow-lg border border-slate-300 dark:border-slate-700">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-slate-800 dark:text-gray-100">
            {isLogin ? 'Sign in to your account' : 'Create a new account'}
          </h2>
        </div>

        {!isLogin && (
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setStudentType('counselling')}
              className={`flex-1 py-2 px-4 rounded-md ${
                studentType === 'counselling' ? 'bg-blue-600 dark:bg-sky-400 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-gray-300'
              }`}
            >
              Counselling Student
            </button>
            <button
              type="button"
              onClick={() => setStudentType('studying')}
              className={`flex-1 py-2 px-4 rounded-md ${
                studentType === 'studying' ? 'bg-blue-600 dark:bg-sky-400 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-gray-300'
              }`}
            >
              Studying Student
            </button>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded whitespace-pre-line">
            <strong>Error:</strong>
            <div className="mt-1">{error}</div>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Name</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Email</label>
                <input
                  type="email"
                  name="email_id"
                  required
                  value={formData.email_id}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Phone Number</label>
                <input
                  type="tel"
                  name="phone_number"
                  required
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                />
              </div>
            </>
          )}

          {isLogin && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Email</label>
              <input
                type="email"
                name="email_id"
                required
                value={formData.email_id}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Password</label>
            <div className="mt-1 relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                className="block w-full px-3 py-2 pr-10 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 dark:text-gray-500 hover:text-slate-600 dark:hover:text-gray-300"
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
            {!isLogin && formData.password && (
              <PasswordStrengthIndicator password={formData.password} />
            )}
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Confirm Password</label>
                <div className="mt-1 relative">
                  <input
                    type={showPasswordConfirm ? "text" : "password"}
                    name="password_confirm"
                    required
                    value={formData.password_confirm}
                    onChange={handleInputChange}
                    className="block w-full px-3 py-2 pr-10 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 dark:text-gray-500 hover:text-slate-600 dark:hover:text-gray-300"
                  >
                    {showPasswordConfirm ? (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
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
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Category</label>
                    <select
                      name="category"
                      required
                      value={formData.category}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
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
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">KCET Rank</label>
                    <input
                      type="number"
                      name="kcet_rank"
                      required
                      value={formData.kcet_rank}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                    />
                  </div>
                </>
              )}

              {studentType === 'studying' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Category</label>
                    <select
                      name="category"
                      required
                      value={formData.category}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                    >
                      <option value="">Select Category</option>
                      {categories.map(cat => (
                        <option key={cat.category} value={cat.category}>
                          {cat.category} ({cat.fall_back})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* College dropdown (replaces text input) */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">College</label>
                    <select
                      name="college_code"
                      required
                      value={formData.college_code}
                      onChange={handleCollegeCodeChange}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                    >
                      <option value="">Select a college</option>
                      {colleges.map((c) => (
                        <option key={c.college_id} value={c.college_code}>
                          {c.college_name} ({c.college_code})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Branch</label>
                    <select
                      name="unique_key"
                      required
                      value={formData.unique_key}
                      onChange={handleInputChange}
                      disabled={!formData.college_code}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 disabled:bg-slate-100 dark:disabled:bg-slate-800 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
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
                    <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">Year of Starting</label>
                    <input
                      type="number"
                      name="year_of_starting"
                      required
                      value={formData.year_of_starting}
                      onChange={handleInputChange}
                      min="2020"
                      max={new Date().getFullYear()}
                      className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
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
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 dark:bg-sky-400 hover:bg-blue-700 dark:hover:bg-sky-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-sky-400 disabled:opacity-50"
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
                setBranches([])
                setColleges([])
                setFormData({
                  name: '',
                  email_id: '',
                  phone_number: '',
                  password: '',
                  password_confirm: '',
                  category: '',
                  kcet_rank: '',
                  college_code: '',
                  unique_key: '',
                  year_of_starting: '',
                })
              }}
              className="text-blue-600 dark:text-sky-400 hover:text-blue-500 dark:hover:text-sky-300"
            >
              {isLogin ? "Don't have an account? Register" : 'Already have an account? Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const PasswordStrengthIndicator = ({ password }: { password: string }) => {
  const { strength, checks } = getPasswordStrength(password)
  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500']

  return (
    <div className="mt-2">
      <div className="flex items-center space-x-2 mb-1">
        <div className="flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${strengthColors[strength - 1] || 'bg-slate-400 dark:bg-slate-600'}`}
            style={{ width: `${(strength / 5) * 100}%` }}
          />
        </div>
        <span className="text-xs text-slate-600 dark:text-gray-400">{strengthLabels[strength - 1] || 'Very Weak'}</span>
      </div>
      <div className="text-xs text-slate-600 dark:text-gray-400 space-y-1">
        <div className={checks.length ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-gray-600'}>✓ At least 8 characters</div>
        <div className={checks.upper ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-gray-600'}>✓ One uppercase letter</div>
        <div className={checks.lower ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-gray-600'}>✓ One lowercase letter</div>
        <div className={checks.number ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-gray-600'}>✓ One number</div>
        <div className={checks.special ? 'text-green-600 dark:text-green-400' : 'text-slate-400 dark:text-gray-600'}>✓ One special character</div>
      </div>
    </div>
  )
}

function getPasswordStrength(password: string) {
  let strength = 0
  const checks = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  }
  strength = Object.values(checks).filter(Boolean).length
  return { strength, checks }
}

export default LoginRegister
