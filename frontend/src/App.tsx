import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import LoginRegister from './pages/LoginRegister'
import CounsellingDashboard from './pages/CounsellingDashboard'
import StudyingDashboard from './pages/StudyingDashboard'
import CollegeDetailPage from './pages/CollegeDetailPage'
import SearchPage from './pages/SearchPage'
import MeetingPage from './pages/MeetingPage'
import ProfilePage from './pages/ProfilePage'
import ProtectedRoute from './components/ProtectedRoute'
// + add this import
import BranchDetailPage from './pages/BranchDetailPage'


function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-slate-50 dark:bg-[#111827]">
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
            <Route path="/branches/:publicId" element={<BranchDetailPage />} />

            <Route path="/colleges/:publicId" element={<CollegeDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route
              path="/meetings"
              element={
                <ProtectedRoute>
                  <MeetingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

