import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { collegeService } from '../services/api'
import type { College } from '../types'

const SearchPage = () => {
  const [query, setQuery] = useState('')
  const [colleges, setColleges] = useState<College[]>([])
  const [loading, setLoading] = useState(false)

  const fetchColleges = async (searchQuery: string) => {
    setLoading(true)
    try {
      const data = await collegeService.search(searchQuery) // returns College[]
      setColleges(data)
    } catch (err) {
      console.error('Error searching colleges:', err)
      setColleges([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // initial: show all colleges
    fetchColleges('')
  }, [])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    await fetchColleges(query.trim())
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold mb-6">Search Colleges</h1>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by college name, code, or location..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {colleges.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Colleges ({colleges.length})</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {colleges.map((college) => (
              <Link
                key={college.college_id}
                to={`/colleges/${college.college_id}`}
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition"
              >
                <h3 className="font-semibold text-lg">{college.college_name}</h3>
                <p className="text-gray-600 text-sm">Code: {college.college_code}</p>
                <p className="text-gray-600 text-sm">Location: {college.location}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {!loading && query && colleges.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No colleges found for “{query}”
        </div>
      )}
    </div>
  )
}

export default SearchPage
