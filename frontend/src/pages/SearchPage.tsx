import { useState } from 'react'
import { Link } from 'react-router-dom'
import { collegeService } from '../services/api'
import type { College, Branch } from '../types'

const SearchPage = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<{ colleges: College[]; branches: Branch[] }>({
    colleges: [],
    branches: [],
  })
  const [loading, setLoading] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const data = await collegeService.search(query)
      setResults(data)
    } catch (err) {
      console.error('Error searching:', err)
      setResults({ colleges: [], branches: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold mb-6">Search Colleges & Branches</h1>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by college name, code, branch, or location..."
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

      {results.colleges.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Colleges ({results.colleges.length})</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {results.colleges.map(college => (
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

      {results.branches.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Branches ({results.branches.length})</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {results.branches.map(branch => (
              <Link
                key={branch.unique_key}
                to={`/colleges/${branch.college.college_id}`}
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition"
              >
                <h3 className="font-semibold text-lg">{branch.branch_name}</h3>
                <p className="text-gray-600 text-sm">{branch.college.college_name}</p>
                <p className="text-gray-600 text-sm">Cluster: {branch.cluster.cluster_name}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {!loading && query && results.colleges.length === 0 && results.branches.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No results found for "{query}"
        </div>
      )}
    </div>
  )
}

export default SearchPage

