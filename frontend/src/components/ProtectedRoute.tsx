import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredType?: 'counselling' | 'studying'
}

const ProtectedRoute = ({ children, requiredType }: ProtectedRouteProps) => {
  const { isAuthenticated, user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />
  }

  if (requiredType && user?.type_of_student !== requiredType) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute

