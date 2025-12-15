import axios from 'axios'
import type { Student, Recommendation, CounsellingChoice, Review, Meeting, College, Branch, Category } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const tokens = getTokens()
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {}

    // If there's no response at all, just bubble up (true network/CORS error)
    if (!error.response) {
      return Promise.reject(error)
    }

    const status = error.response.status
    const url: string = originalRequest.url || ''

    // Do NOT attempt refresh for auth endpoints themselves
    const isAuthEndpoint =
      url.includes('/auth/login/') ||
      url.includes('/auth/register/') ||
      url.includes('/auth/refresh/')

    if (status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true

      try {
        const tokens = getTokens()
        if (tokens?.refresh) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: tokens.refresh,
          })
          const newTokens = {
            access: response.data.access,
            // keep using the same refresh token (backend rotates internally if configured)
            refresh: tokens.refresh,
          }
          setTokens(newTokens)
          if (!originalRequest.headers) originalRequest.headers = {}
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`
          return api(originalRequest)
        }
      } catch (refreshError: any) {
        // Refresh failed, clear auth and send user to login
        clearTokens()
        window.location.href = '/auth'
        // Attach a clearer message so UI doesn't just show "Network Error"
        if (!refreshError.response) {
          refreshError.message = refreshError.message || 'Session expired. Please log in again.'
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

function getTokens() {
  const stored = localStorage.getItem('tokens')
  return stored ? JSON.parse(stored) : null
}

function setTokens(tokens: { access: string; refresh: string }) {
  localStorage.setItem('tokens', JSON.stringify(tokens))
}

function clearTokens() {
  localStorage.removeItem('tokens')
  localStorage.removeItem('user')
}

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email_id: email, password })
    return response.data
  },

  register: async (data: any) => {
    const response = await api.post('/auth/register/', data)
    return response.data
  },

  me: async (): Promise<Student> => {
    const response = await api.get('/auth/me/')
    return response.data
  },

  updateProfile: async (data: Partial<Student>): Promise<Student> => {
    const response = await api.patch('/auth/profile/', data)
    return response.data
  },

  refresh: async (refreshToken: string) => {
    const response = await api.post('/auth/refresh/', { refresh: refreshToken })
    return response.data
  },

  setTokens,
  clearTokens,
}

// // services/api.ts  (replace existing collegeService block with this)
// import api from './apiInstance' // <-- if you export `api` as axios instance; else use your `api` variable here
// // or if api is in same file skip the import (keep the axios instance you already have)

export const collegeService = {
  list: async (): Promise<College[]> => {
    const response = await api.get('/colleges/')
    return response.data
  },

  detail: async (collegeId: string): Promise<College & { branches: Branch[] }> => {
    const response = await api.get(`/colleges/${collegeId}/`)
    return response.data
  },

  cutoff: async (collegeId: string) => {
    const response = await api.get(`/colleges/${collegeId}/cutoff/`)
    return response.data
  },

  /**
   * search(params)
   * - Accepts { query?, location? }
   * - Calls your Django /search/ endpoint which returns { colleges, branches, locations }
   * - Returns an array of colleges (frontend expects College[])
   */
  search: async (params: { query?: string; location?: string } = {}): Promise<College[]> => {
    const res = await api.get('/search/', { params })
    // backend returns { colleges, branches, locations } — prefer colleges
    if (res?.data?.colleges && Array.isArray(res.data.colleges)) return res.data.colleges as College[]
    // fallback: if the endpoint returns an array directly
    if (Array.isArray(res.data)) return res.data as College[]
    return []
  },

  /**
   * getLocations()
   * - Calls /locations/ (lightweight) and handles either:
   *    { locations: [...] }  OR  plain array ["City1","City2"]
   */
  getLocations: async (): Promise<string[]> => {
    try {
      const res = await api.get('/locations/')
      if (res?.data?.locations && Array.isArray(res.data.locations)) return res.data.locations
      if (Array.isArray(res.data)) return res.data
      // unexpected shape -> try search fallback
    } catch (err) {
      // fall through to fallback below
      console.warn('/locations/ failed, trying /search/ fallback', err)
    }

    // Fallback: call /search/ and read locations or derive from colleges
    try {
      const res2 = await api.get('/search/', { params: {} })
      if (res2?.data?.locations && Array.isArray(res2.data.locations)) return res2.data.locations
      if (Array.isArray(res2?.data?.colleges)) {
        const dedup = Array.from(new Set(res2.data.colleges.map((c: any) => (c.location || '').trim()).filter(Boolean)))
        return dedup.sort()
      }
    } catch (err) {
      console.error('Fallback /search/ also failed when fetching locations', err)
    }

    return []
  }
}


export const branchService = {
  detail: async (uniqueKey: string): Promise<Branch> => {
    const response = await api.get(`/branches/${uniqueKey}/`)
    return response.data
  },

  byCollegeCode: async (collegeCode: string): Promise<Branch[]> => {
    const response = await api.get(`/branches/by-code/${collegeCode}/`)
    return response.data
  },

  cutoff: async (uniqueKey: string, category?: string) => {
    const params = category ? { category } : {}
    const response = await api.get(`/branches/${uniqueKey}/cutoff/`, { params })
    return response.data
  },
}

export const counsellingService = {
  recommendations: async (kcetRank: number, category?: string, year?: string, openingRank?: number, closingRank?: number): Promise<{
    recommendations: Recommendation[]
    count: number
  }> => {
    const response = await api.post('/counselling/recommendations/', {
      kcet_rank: kcetRank,
      category,
      year: year || '2025',
      opening_rank: openingRank,
      closing_rank: closingRank,
    })
    return response.data
  },

  choices: {
    list: async (): Promise<CounsellingChoice[]> => {
      const response = await api.get('/counselling/choices/')
      return response.data
    },

    create: async (uniqueKey: string, orderOfList?: number): Promise<CounsellingChoice> => {
      const payload: Record<string, any> = { unique_key: uniqueKey }
      if (orderOfList !== undefined) {
        payload.order_of_list = orderOfList
      }
      const response = await api.post('/counselling/choices/create/', payload)
      return response.data
    },

    update: async (choiceId: number, orderOfList: number): Promise<CounsellingChoice> => {
      const response = await api.patch(`/counselling/choices/${choiceId}/update/`, {
        order_of_list: orderOfList,
      })
      return response.data
    },

    bulkUpdate: async (choices: Array<{ choice_id: number; order_of_list: number }>): Promise<CounsellingChoice[]> => {
      const response = await api.post('/counselling/choices/bulk-update/', {
        choices: choices,
      })
      return response.data
    },

    delete: async (choiceId: number): Promise<void> => {
      await api.delete(`/counselling/choices/${choiceId}/delete/`)
    },
  },
}

export const reviewService = {
  create: async (data: Partial<Review>): Promise<Review> => {
    const response = await api.post('/reviews/', data)
    return response.data
  },

  myReview: async (uniqueKey: string): Promise<Review | null> => {
    const response = await api.get(`/reviews/my-review/${uniqueKey}/`)
    const data = response.data
    if (data === null) return null
    if (typeof data === 'object' && 'review' in data) {
      return data.review || null
    }
    return data as Review
  },

  delete: async (uniqueKey: string): Promise<void> => {
    await api.delete(`/reviews/my-review/${uniqueKey}/delete/`)
  },

  branchReviews: async (uniqueKey: string): Promise<{
    reviews: Review[]
    average_ratings: Record<string, number>
    total_reviews: number
  }> => {
    const response = await api.get(`/reviews/branches/${uniqueKey}/`)
    return response.data
  },

  collegeReviews: async (collegeId: string) => {
    const response = await api.get(`/reviews/colleges/${collegeId}/`)
    return response.data
  },
}

export const meetingService = {
  request: async (studyingUserId: string, scheduledTime?: string): Promise<Meeting> => {
    const response = await api.post('/meetings/request/', {
      studying_user_id: studyingUserId,
      scheduled_time: scheduledTime,
    })
    return response.data
  },

  myRequests: async (): Promise<Meeting[]> => {
    const response = await api.get('/meetings/my-requests/')
    return response.data
  },

  myInvitations: async (): Promise<Meeting[]> => {
    const response = await api.get('/meetings/my-invitations/')
    return response.data
  },

  updateStatus: async (meetingId: number, status: string, scheduledTime?: string): Promise<Meeting> => {
    const response = await api.patch(`/meetings/${meetingId}/status/`, {
      status,
      scheduled_time: scheduledTime,
    })
    return response.data
  },

  branchStudents: async (uniqueKey: string) => {
    const response = await api.get(`/meetings/branches/${uniqueKey}/students/`)
    return response.data
  },
}

export const categoryService = {
  list: async (): Promise<Category[]> => {
    try {
      const response = await api.get('/colleges/categories/')
      return response.data
    } catch (error) {
      // Fallback to hardcoded categories if API fails
      console.warn('Failed to load categories from API, using fallback list')
      const { HARDCODED_CATEGORIES } = await import('../data/categories')
      return HARDCODED_CATEGORIES
    }
  },
}

