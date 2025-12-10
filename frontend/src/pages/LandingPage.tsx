import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import logo from '../assets/logo.png'

// Swiper
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";

const LandingPage = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen">

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-[#AEE1D9] to-[#7CC6D9] 
                dark:from-[#0F3D3E] dark:to-[#14505B] text-[#003F41] dark:text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center flex flex-col items-center">
            <img 
              src={logo}
              alt="KCET EduGuide Logo" 
              className="h-20 w-auto object-contain mb-4" 
            />
            <h1
              className="text-5xl font-bold mb-6"
              style={{ fontFamily: "Dancing Script, cursive" }}
            >
              KCET EduGuide
            </h1>

            <p className="text-xl mb-8 text-white">
              Your comprehensive guide to finding the perfect college and branch based on your KCET rank
            </p>

            {!isAuthenticated && (
              <Link
                to="/auth"
                className="backdrop-blur-md bg-white/20 text-white px-8 py-3 rounded-xl text-lg font-semibold border border-white/30 hover:bg-white/30 transition"
              >
                Get Started
              </Link>
            )}

            {isAuthenticated && (
              <Link
                to={user?.type_of_student === "counselling" ? "/dashboard/counselling" : "/dashboard/studying"}
                className="backdrop-blur-md bg-white/20 text-white px-8 py-3 rounded-xl text-lg font-semibold border border-white/30 hover:bg-white/30 transition"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-slate-800 dark:text-gray-100">
          How It Works
        </h2>

        <Swiper
          modules={[Pagination, Autoplay]}
          spaceBetween={30}
          slidesPerView={1}
          loop={true}
          pagination={{ clickable: true }}
          autoplay={{ delay: 2500 }}
          className="w-full max-w-4xl mx-auto"
        >

          {/* Slide 1 */}
          <SwiperSlide>
            <div className="bg-white dark:bg-slate-800 p-10 rounded-xl shadow-lg 
                            border border-slate-300 dark:border-slate-700 text-center">

              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <svg className="w-16 h-16 text-teal-600 dark:text-teal-300" fill="none" 
                    stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" 
                        d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path strokeLinecap="round" strokeLinejoin="round" 
                        d="M19.5 21a8.38 8.38 0 00-15-5.13M12 3v3m0 12v3m9-9h-3M6 12H3"/>
                </svg>
              </div>

              <h3 className="text-2xl font-bold mb-3 text-slate-800 dark:text-gray-100">
                Enter Your Rank
              </h3>

              <p className="text-slate-600 dark:text-gray-400 text-lg">
                Provide your KCET rank to instantly receive personalized college & branch 
                predictions based on verified historical cutoff data.
              </p>
              <ul className="text-slate-600 dark:text-gray-400 text-left mt-4 space-y-2 text-lg">
                <li>• Get accurate admission chances</li>
                <li>• Discover branches you are eligible for</li>
                <li>• Compare opportunities based on rank</li>
              </ul>
            </div>
          </SwiperSlide>

          {/* Slide 2 */}
          <SwiperSlide>
            <div className="bg-white dark:bg-slate-800 p-10 rounded-xl shadow-lg 
                            border border-slate-300 dark:border-slate-700 text-center">

              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <svg className="w-16 h-16 text-blue-600 dark:text-blue-300" fill="none"
                    stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" 
                        d="M21 21l-4.35-4.35M11 6a5 5 0 100 10 5 5 0 000-10z"/>
                </svg>
              </div>

              <h3 className="text-2xl font-bold mb-3 text-slate-800 dark:text-gray-100">
                Explore Your Best Options
              </h3>

              <p className="text-slate-600 dark:text-gray-400 text-lg">
                Analyze recommendations, study cutoff trends, read real student reviews, 
                and compare colleges side-by-side to make informed decisions.
              </p>
              <ul className="text-slate-600 dark:text-gray-400 text-left mt-4 space-y-2 text-lg">
                <li>• Visualize year-wise cutoff trends</li>
                <li>• Read real student experiences</li>
                <li>• Save & compare colleges side-by-side</li>
                <li>• Filter by location, fees, or college code</li>
              </ul>
            </div>
          </SwiperSlide>


          {/* Slide 3 */}
          <SwiperSlide>
            <div className="bg-white dark:bg-slate-800 p-10 rounded-xl shadow-lg 
                            border border-slate-300 dark:border-slate-700 text-center">

              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <svg className="w-16 h-16 text-indigo-600 dark:text-indigo-300" fill="none"
                    stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" 
                        d="M15 19a3 3 0 10-6 0M12 14a5 5 0 100-10 5 5 0 000 10z"/>
                  <path strokeLinecap="round" strokeLinejoin="round"
                        d="M19 20v-2a5 5 0 00-5-5H10a5 5 0 00-5 5v2"/>
                </svg>
              </div>

              <h3 className="text-2xl font-bold mb-3 text-slate-800 dark:text-gray-100">
                Connect With Seniors
              </h3>

              <p className="text-slate-600 dark:text-gray-400 text-lg">
                Ask doubts, gather real insights, and schedule meetings with seniors for 
                trusted guidance about branches and colleges.
              </p>
              <ul className="text-slate-600 dark:text-gray-400 text-left mt-4 space-y-2 text-lg">
                <li>• Ask doubts about branches & colleges</li>
                <li>• Understand placements, faculty & campus life</li>
                <li>• Receive real guidance from real students</li>
              </ul>
            </div>
          </SwiperSlide>

          {/* Slide 4 */}
          <SwiperSlide>
            <div className="bg-white dark:bg-slate-800 p-10 rounded-xl shadow-lg
                            border border-slate-300 dark:border-slate-700 text-center">

              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <svg className="w-16 h-16 text-emerald-600 dark:text-emerald-300" fill="none"
                    stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" 
                        d="M12 4.5v15m7.5-7.5h-15"/>
                </svg>
              </div>

              <h3 className="text-2xl font-bold mb-3 text-slate-800 dark:text-gray-100">
                Build Your Profile
              </h3>

              <p className="text-slate-600 dark:text-gray-400 text-lg">
                Save favourites, track your shortlists, and receive personalized counselling 
                insights tailored to your preferences.
              </p>
              <ul className="text-slate-600 dark:text-gray-400 text-left mt-4 space-y-2 text-lg">
                <li>• Save favourite colleges & branches</li>
                <li>• Track your analysis & choices anytime</li>
                <li>• Receive personalized guidance</li>
              </ul>

            </div>
          </SwiperSlide>

        </Swiper>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border-t border-yellow-200 dark:border-yellow-800 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 text-center">
            <strong>Disclaimer:</strong> The cutoffs are taken only from the official KCET counselling website. 
            For further confirmation, you may visit the official KCET website.
          </p>
        </div>
      </div>

    </div>
  );
};

export default LandingPage;
