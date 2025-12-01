import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import LoginRegister from './pages/LoginRegister'
import CounsellingDashboard from './pages/CounsellingDashboard'
import StudyingDashboard from './pages/StudyingDashboard'
import CollegeDetailPage from './pages/CollegeDetailPage'
import SearchPage from './pages/SearchPage'
import MeetingPage from './pages/MeetingPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth" element={<LoginRegister />} />
            <Route
              path="/dashboard/counselling"
              element={
                <ProtectedRoute requiredType="counselling">
                  <CounsellingDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/studying"
              element={
                <ProtectedRoute requiredType="studying">
                  <StudyingDashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/colleges/:collegeId" element={<CollegeDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route
              path="/meetings"
              element={
                <ProtectedRoute>
                  <MeetingPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

