import { useAdminAuth } from '../../contexts/AdminAuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import BranchInsightUpload from '../../components/admin/BranchInsightUpload'
import { useNavigate } from 'react-router-dom'

export default function AdminDashboard() {
  const { admin, logout } = useAdminAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#111827]">
      <header className="border-b border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-lg font-semibold text-slate-900 dark:text-white">Admin Dashboard</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Signed in as {admin?.email}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700 dark:border-slate-600 dark:text-slate-200"
            >
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
            <button
              type="button"
              onClick={() => {
                logout()
                navigate('/admin/login')
              }}
              className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium text-white dark:bg-slate-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        <BranchInsightUpload />
      </main>
    </div>
  )
}
