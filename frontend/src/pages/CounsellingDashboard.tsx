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
  const [openingRank, setOpeningRank] = useState<number>(0)
  const [closingRank, setClosingRank] = useState<number>(0)
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [saving, setSaving] = useState(false)
  const [exportingPdf, setExportingPdf] = useState(false)

  // compute the best display name once
  const displayName = useMemo(() => {
    // 1) if backend sent a name, show first name
    const full = user?.name?.trim();
    if (full) return full;

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
    // Initialize opening and closing ranks based on user's rank
    if (user?.kcet_rank) {
      setOpeningRank(Math.floor(user.kcet_rank * 0.5))
      setClosingRank(Math.floor(user.kcet_rank * 1.75))
    }
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
        openingRank,
        closingRank,
      )
      setRecommendations(data.recommendations)
      setShowRecommendations(true)
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error loading recommendations')
    } finally {
      setLoading(false)
    }
  }

  // Check if a branch is already in choices
  const isInChoices = (uniqueKey: string): boolean => {
    return choices.some(choice => choice.unique_key === uniqueKey)
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
        <h1 className="text-3xl font-bold text-slate-800 dark:text-gray-100">Counselling Dashboard</h1>
        <>
        <p className="mt-1 text-slate-700 dark:text-gray-300">
          <strong>Welcome,</strong> {displayName}
        </p>
        <p className='text-slate-600 dark:text-gray-400'>
          <strong>Your KCET Rank :</strong> {user?.kcet_rank || <span className="text-red-600 dark:text-red-400">'Not set'</span>}
        </p>
        </>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        {/* Reduced Quick Actions size */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <h2 className="text-lg font-semibold mb-3 text-slate-800 dark:text-gray-100">Quick Actions</h2>
          <div className="space-y-2">
            <button
              onClick={loadRecommendations}
              disabled={loading}
              className="w-full bg-blue-600 dark:bg-sky-400 text-white px-3 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-sky-500 disabled:opacity-50 text-sm"
            >
              {loading ? 'Loading...' : 'View Recommendations'}
            </button>
            <Link
              to="/search"
              className="block w-full bg-slate-600 dark:bg-slate-500 text-white px-3 py-2 rounded-md hover:bg-slate-700 dark:hover:bg-slate-600 text-center text-sm"
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
        <div className="md:col-span-3 bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-gray-100">
              My Personal List ({choices.length})
            </h2>
            <div className="flex gap-2">
              <button
                onClick={exportChoicesToPdf}
                disabled={exportingPdf}
                className="bg-slate-400 dark:bg-slate-600 border border-slate-700 dark:border-slate-500 text-white px-3 py-2 rounded-md hover:bg-slate-500 dark:hover:bg-slate-700 text-sm"
              >
                {exportingPdf ? 'Preparing PDF...' : '⬇️ Download PDF'}
              </button>
              {hasUnsavedChanges && (
                <button
                  onClick={handleSaveOrder}
                  disabled={saving}
                  className="bg-blue-600 dark:bg-sky-400 text-white px-4 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-sky-500 disabled:opacity-50 text-sm"
                >
                  {saving ? 'Saving...' : 'Save Order'}
                </button>
              )}
            </div>
          </div>

          {choices.length === 0 ? (
            <p className="text-slate-500 dark:text-gray-400">No choices saved yet</p>
          ) : (
            <div className="overflow-x-auto">
              <div className="max-h-[37rem] overflow-y-auto">
              <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                <thead className="bg-slate-50 dark:bg-slate-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase w-16">
                      Order
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      College Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Branch
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Cluster
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Cutoff
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase w-20">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                  {choices.map((choice, index) => (
                    <tr
                      key={choice.choice_id}
                      draggable
                      onDragStart={() => handleDragStart(index)}
                      onDragOver={(e) => handleDragOver(e, index)}
                      onDragEnd={handleDragEnd}
                      className={`hover:bg-slate-50 dark:hover:bg-slate-700 cursor-move ${
                        draggedIndex === index ? 'opacity-50' : ''
                      }`}
                    >
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-gray-100">
                        {index + 1}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-gray-100">
                        <Link
                          to={`/colleges/${choice.unique_key_data?.college.college_id || ''}`}
                          className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300 hover:underline cursor-pointer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {choice.unique_key_data?.college.college_name || 'N/A'}
                        </Link>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-gray-100">
                        <Link
                          to={`/branches/${choice.unique_key || ''}`}
                          className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300 hover:underline cursor-pointer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {choice.unique_key_data?.branch_name || 'N/A'}
                        </Link>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-gray-100">
                        {choice.unique_key_data?.cluster.cluster_name || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-gray-100">
                        {choice.cutoff || 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => removeChoice(choice.choice_id)}
                          className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {showRecommendations && (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md border border-slate-300 dark:border-slate-700">
          <div className="mb-4 flex flex-wrap gap-4 items-center">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-gray-100">Recommendations</h2>
            <select
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="border border-slate-300 dark:border-slate-600 rounded px-3 py-1 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.category} value={cat.category}>
                  {cat.category}
                </option>
              ))}
            </select>
             <select
               value={year}
               onChange={e => setYear(e.target.value)}
               className="border border-slate-300 dark:border-slate-600 rounded px-3 py-1 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
             >
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
            </select>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Opening Rank:</label>
              <input
                type="number"
                value={openingRank}
                onChange={e => setOpeningRank(Number(e.target.value))}
                className="border border-slate-300 dark:border-slate-600 rounded px-3 py-1 w-24 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                min="0"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Closing Rank:</label>
              <input
                type="number"
                value={closingRank}
                onChange={e => setClosingRank(Number(e.target.value))}
                className="border border-slate-300 dark:border-slate-600 rounded px-3 py-1 w-24 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
                min="0"
              />
            </div>
            <button
              onClick={loadRecommendations}
              className="bg-blue-600 dark:bg-sky-400 text-white px-4 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-sky-500"
            >
              Refresh
            </button>
          </div>

          {recommendations.length === 0 ? (
            <p className="text-slate-500 dark:text-gray-400">No recommendations found</p>
          ) : (
            <div className="overflow-x-auto">
              <div className="max-h-[40em] overflow-y-auto">
              <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                <thead className="bg-slate-50 dark:bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      College
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Branch
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Round 1 Cutoff
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Round 3 Cutoff
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Distance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-gray-400 uppercase">
                      Action
                    </th>
                  </tr>
                </thead>
                 <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                   {recommendations.map(rec => (
                    <tr key={rec.unique_key} className="hover:bg-slate-50 dark:hover:bg-slate-700">
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">
                        <Link
                          to={`/colleges/${rec.college.college_id}`}
                          className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300 hover:underline cursor-pointer"
                        >
                          {rec.college.college_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">
                        <Link
                          to={`/branches/${rec.unique_key}`}
                          className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300 hover:underline cursor-pointer"
                        >
                          {rec.branch.branch_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">{rec.opening_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">{rec.closing_rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">
                        {rec.distance_from_rank}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-900 dark:text-gray-100">
                        {isInChoices(rec.unique_key) ? (
                          <span className="px-2 py-1 bg-slate-200 dark:bg-slate-600 text-slate-600 dark:text-gray-300 rounded text-sm cursor-not-allowed">
                            Added
                          </span>
                        ) : (
                          <button
                            onClick={() => addToChoices(rec.unique_key)}
                            className="text-blue-600 dark:text-sky-400 hover:text-blue-800 dark:hover:text-sky-300"
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
          )}
        </div>
      )}
    </div>
  )
}

export default CounsellingDashboard
