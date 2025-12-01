import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const LandingPage = () => {
  const { isAuthenticated, user } = useAuth()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              KCET EduGuide
            </h1>
            <p className="text-xl mb-8 text-primary-100">
              Your comprehensive guide to finding the perfect college and branch based on your KCET rank
            </p>
            {!isAuthenticated && (
              <Link
                to="/auth"
                className="bg-white text-primary-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-primary-50 transition"
              >
                Get Started
              </Link>
            )}
            {isAuthenticated && (
              <Link
                to={user?.type_of_student === 'counselling' ? '/dashboard/counselling' : '/dashboard/studying'}
                className="bg-white text-primary-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-primary-50 transition"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">1️⃣</div>
            <h3 className="text-xl font-semibold mb-2">Enter Your Rank</h3>
            <p className="text-gray-600">
              Input your KCET rank and get personalized college and branch recommendations based on historical cutoff data.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">2️⃣</div>
            <h3 className="text-xl font-semibold mb-2">Explore Options</h3>
            <p className="text-gray-600">
              Browse through recommended colleges, view cutoff trends, read reviews from current students, and save your preferences.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">3️⃣</div>
            <h3 className="text-xl font-semibold mb-2">Connect with Seniors</h3>
            <p className="text-gray-600">
              Schedule meetings with current students to get first-hand insights about colleges and branches.
            </p>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-gray-100 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-lg mb-2">How accurate are the recommendations?</h3>
              <p className="text-gray-600">
                Our recommendations are based on historical cutoff data from previous years. While we strive for accuracy,
                actual cutoffs may vary. Always verify with official sources.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-lg mb-2">Can I use this if I'm already in college?</h3>
              <p className="text-gray-600">
                Yes! If you're a current student, you can register as a "Studying Student" to share reviews and help
                counselling students make informed decisions.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-lg mb-2">How do meetings work?</h3>
              <p className="text-gray-600">
                Counselling students can request meetings with studying students. Once accepted, a Google Meet link is
                automatically generated and sent to both parties.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border-t border-yellow-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-sm text-yellow-800 text-center">
            <strong>Disclaimer:</strong> The cutoff data and recommendations provided are for informational purposes only.
            Always refer to official KCET counseling websites for the most accurate and up-to-date information.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LandingPage

