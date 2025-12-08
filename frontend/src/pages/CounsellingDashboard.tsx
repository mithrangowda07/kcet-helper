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
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [saving, setSaving] = useState(false)
  const [exportingPdf, setExportingPdf] = useState(false)

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
      setHasUnsavedChanges(false)
    } catch (err) {
      console.error('Error loading choices:', err)
    }
  }

  const loadCategories = async () => {
    try {
      const data = await categoryService.list()
      setCategories(data)
    } catch (err) {
      console.error('Error loading categories, using fallback:', err)
      // Fallback to hardcoded categories
      try {
        const { HARDCODED_CATEGORIES } = await import('../data/categories')
        setCategories(HARDCODED_CATEGORIES)
      } catch {
        setCategories([])
      }
    }
  }

  const handleDragStart = (index: number) => {
    setDraggedIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggedIndex === null) return

    if (draggedIndex !== index) {
      const newChoices = [...choices]
      const draggedItem = newChoices[draggedIndex]
      newChoices.splice(draggedIndex, 1)
      newChoices.splice(index, 0, draggedItem)
      setChoices(newChoices)
      setDraggedIndex(index)
      setHasUnsavedChanges(true)
    }
  }

  const handleDragEnd = () => {
    setDraggedIndex(null)
  }

  const handleSaveOrder = async () => {
    setSaving(true)
    try {
      const choicesToUpdate = choices.map((choice, index) => ({
        choice_id: choice.choice_id,
        order_of_list: index + 1,
      }))
      await counsellingService.choices.bulkUpdate(choicesToUpdate)
      await loadChoices()
      alert('Order saved successfully!')
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error saving order')
    } finally {
      setSaving(false)
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
      await counsellingService.choices.create(uniqueKey)
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

  const exportChoicesToPdf = async () => {
    if (!choices.length) {
      alert('No choices to export yet')
      return
    }

    setExportingPdf(true)
    try {
      const [{ default: jsPDF }, autoTableModule] = await Promise.all([
        import('jspdf'),
        import('jspdf-autotable'),
      ])
      const autoTable = autoTableModule.default
      const doc = new jsPDF({ orientation: 'landscape' })

      doc.setFontSize(16)
      doc.text('KCET Helper - My Personal List', 14, 14)
      doc.setFontSize(10)
      doc.text(`Total choices: ${choices.length}`, 14, 22)

      autoTable(doc, {
        startY: 28,
        head: [['#', 'College', 'Branch', 'Cluster', 'Cutoff']],
        body: choices.map((choice, idx) => [
          idx + 1,
          choice.unique_key_data?.college.college_name || 'N/A',
          choice.unique_key_data?.branch_name || 'N/A',
          choice.unique_key_data?.cluster.cluster_name || 'N/A',
          choice.cutoff || 'N/A',
        ]),
        styles: { halign: 'left' },
        headStyles: { fillColor: [22, 101, 52] },
        alternateRowStyles: { fillColor: [245, 245, 245] },
        columnStyles: {
          0: { cellWidth: 12, halign: 'center' },
          4: { cellWidth: 25, halign: 'center' },
        },
      })

      // watermark on every page
      const pageCount = doc.getNumberOfPages()
      for (let i = 1; i <= pageCount; i += 1) {
        doc.setPage(i)
        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        doc.setTextColor(220, 220, 220)
        doc.setFontSize(48)
        doc.text('KCET-Helper', pageWidth / 2, pageHeight / 2, {
          angle: -30,
          align: 'center',
        })
      }

      doc.save('kcet-helper-choices.pdf')
    } catch (err) {
      console.error('PDF export failed', err)
      alert('Could not generate PDF. Please try again.')
    } finally {
      setExportingPdf(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Counselling Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome, {displayName}.{' '}
          Your KCET Rank: <strong>{user?.kcet_rank || 'Not set'}</strong>
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        {/* Reduced Quick Actions size */}
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
          <div className="space-y-2">
            <button
              onClick={loadRecommendations}
              disabled={loading}
              className="w-full bg-primary-600 text-white px-3 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 text-sm"
            >
              {loading ? 'Loading...' : 'View Recommendations'}
            </button>
            <Link
              to="/search"
              className="block w-full bg-gray-600 text-white px-3 py-2 rounded-md hover:bg-gray-700 text-center text-sm"
            >
              Search Colleges
            </Link>
            <Link
              to="/meetings"
              className="block w-full bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 text-center text-sm"
            >
              Meet Seniors
            </Link>
          </div>
        </div>

        {/* Personal List Table - Takes more space */}
        <div className="md:col-span-3 bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              My Personal List ({choices.length})
            </h2>
            <div className="flex gap-2">
              <button
                onClick={exportChoicesToPdf}
                disabled={exportingPdf}
                className="bg-white border border-gray-300 text-gray-800 px-3 py-2 rounded-md hover:bg-gray-50 text-sm"
              >
                {exportingPdf ? 'Preparing PDF...' : 'Download PDF'}
              </button>
              {hasUnsavedChanges && (
                <button
                  onClick={handleSaveOrder}
                  disabled={saving}
                  className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 text-sm"
                >
                  {saving ? 'Saving...' : 'Save Order'}
                </button>
              )}
            </div>
          </div>

          {choices.length === 0 ? (
            <p className="text-gray-500">No choices saved yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-16">
                      Order
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      College Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Branch
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Cluster
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Cutoff
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-20">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {choices.map((choice, index) => (
                    <tr
                      key={choice.choice_id}
                      draggable
                      onDragStart={() => handleDragStart(index)}
                      onDragOver={(e) => handleDragOver(e, index)}
                      onDragEnd={handleDragEnd}
                      className={`hover:bg-gray-50 cursor-move ${
                        draggedIndex === index ? 'opacity-50' : ''
                      }`}
                    >
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {index + 1}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {choice.unique_key_data?.college.college_name || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {choice.unique_key_data?.branch_name || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {choice.unique_key_data?.cluster.cluster_name || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {choice.cutoff || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => removeChoice(choice.choice_id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
