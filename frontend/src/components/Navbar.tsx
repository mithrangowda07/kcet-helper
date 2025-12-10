import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import logo from '../assets/logo.png'

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    if (path === '/dashboard/counselling' || path === '/dashboard/studying') {
      return location.pathname === '/dashboard/counselling' || location.pathname === '/dashboard/studying'
    }
    return location.pathname === path
  }

  const getLinkClasses = (path: string) => {
    const active = isActive(path)
    return `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      active
        ? 'text-blue-600 dark:text-sky-400 font-semibold'
        : 'text-slate-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-sky-400'
    }`
  }

  return (
    <nav className="bg-white dark:bg-slate-800 shadow-lg border-b border-slate-300 dark:border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <img 
                src={logo}
                alt="KCET EduGuide Logo" 
                className="h-12 w-30 object-contain" 
              />
              <span 
                className="text-2xl font-bold text-blue-600 dark:text-sky-400"
                style={{ fontFamily: 'Dancing Script, cursive' }}
              >
                KCET EduGuide
              </span>
            </Link>
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              <Link
                to="/"
                className={getLinkClasses('/')}
              >
                Home
              </Link>
              <Link
                to="/search"
                className={getLinkClasses('/search')}
              >
                Search Colleges
              </Link>
              {isAuthenticated && (
                <Link
                  to={user?.type_of_student === 'counselling' ? '/dashboard/counselling' : '/dashboard/studying'}
                  className={getLinkClasses('/dashboard/counselling')}
                >
                  Dashboard
                </Link>
              )}
              {isAuthenticated && (
                <Link
                  to="/meetings"
                  className={getLinkClasses('/meetings')}
                >
                  Meetings
                </Link>
              )}
              {isAuthenticated && (
                <Link
                  to="/profile"
                  className={getLinkClasses('/profile')}
                >
                  Profile
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-slate-700 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
            {isAuthenticated ? (
              <>
                <span className="text-slate-700 dark:text-gray-300 text-sm">
                  {user?.name || user?.email_id}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/auth"
                className="bg-blue-600 hover:bg-blue-700 dark:bg-sky-400 dark:hover:bg-sky-500 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Login / Register
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

