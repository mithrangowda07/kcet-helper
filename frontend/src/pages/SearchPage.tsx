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
      <h1 className="text-3xl font-bold mb-6 text-slate-800 dark:text-gray-100">Search Colleges</h1>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by college name, code, or location..."
            className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200 placeholder-slate-400 dark:placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 dark:bg-sky-400 text-white px-6 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-sky-500 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {colleges.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-gray-100">Colleges ({colleges.length})</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {colleges.map((college) => (
              <Link
                key={college.college_id}
                to={`/colleges/${college.college_id}`}
                className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-md hover:shadow-lg transition border border-slate-300 dark:border-slate-700"
              >
                <h3 className="font-semibold text-lg text-slate-800 dark:text-gray-100">{college.college_name}</h3>
                <p className="text-slate-600 dark:text-gray-400 text-sm">Code: {college.college_code}</p>
                <p className="text-slate-600 dark:text-gray-400 text-sm">Location: {college.location}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {!loading && query && colleges.length === 0 && (
        <div className="text-center py-12 text-slate-500 dark:text-gray-400">
          No colleges found for "{query}"
        </div>
      )}
    </div>
  )
}

export default SearchPage
