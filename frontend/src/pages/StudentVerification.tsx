import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { studentVerificationService, collegeService } from "../services/api";
import type { College } from "../types";

interface VerificationData {
  college_name: string;
  student_name: string;
  usn: string;
  id_image: File | null;
}

const StudentVerification = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<VerificationData>({
    college_name: "",
    student_name: "",
    usn: "",
    id_image: null,
  });
  const [colleges, setColleges] = useState<College[]>([]);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [verificationScores, setVerificationScores] = useState<{
    college: number;
    name: number;
    usn: number;
  } | null>(null);

  // Load colleges on component mount
  useEffect(() => {
    collegeService
      .list()
      .then(setColleges)
      .catch((err) => {
        console.error("Error loading colleges:", err);
        setError("Failed to load colleges. Please refresh the page.");
      });
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
    setVerificationScores(null);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        setError("Please upload an image file");
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError("Image size must be less than 5MB");
        return;
      }

      setFormData((prev) => ({ ...prev, id_image: file }));
      setError("");
      setVerificationScores(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setVerificationScores(null);

    // Validate form
    if (!formData.college_name.trim()) {
      setError("College name is required");
      setLoading(false);
      return;
    }
    if (!formData.student_name.trim()) {
      setError("Student name is required");
      setLoading(false);
      return;
    }
    if (!formData.usn.trim()) {
      setError("USN/Student ID is required");
      setLoading(false);
      return;
    }
    if (!formData.id_image) {
      setError("Please upload your college ID image");
      setLoading(false);
      return;
    }

    try {
      const result = await studentVerificationService.verify(
        formData.college_name,
        formData.student_name,
        formData.usn,
        formData.id_image
      );

      // Update verification scores with new format
      if (result.college_score !== undefined) {
        setVerificationScores({
          college: result.college_score / 100, // Convert to 0-1 range for display
          name: result.name_score / 100,
          usn: result.usn_score / 100,
        });
      }

      if (result.verified) {
        // Store verification data in sessionStorage for registration
        sessionStorage.setItem("verified_student", JSON.stringify({
          college_name: formData.college_name,
          student_name: formData.student_name,
          usn: formData.usn,
          verified: true,
          image_base64: result.image_base64, // Store image in session
        }));

        // Navigate to registration page
        navigate("/auth?type=studying&verified=true");
      } else {
        setError(
          result.message ||
            "Verification failed. Please ensure all information matches your ID card."
        );
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        "Verification failed. Please try again.";
      setError(errorMessage);
      
      // Handle new response format
      if (err.response?.data?.college_score !== undefined) {
        setVerificationScores({
          college: err.response.data.college_score / 100,
          name: err.response.data.name_score / 100,
          usn: err.response.data.usn_score / 100,
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#111827] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white dark:bg-slate-800 p-8 rounded-lg shadow-lg border border-slate-300 dark:border-slate-700">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-slate-800 dark:text-gray-100">
            Student Verification
          </h2>
          <p className="mt-2 text-center text-sm text-slate-600 dark:text-gray-400">
            Please upload your college ID to verify your student status
          </p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded">
            <strong>Error:</strong> {error}
            {verificationScores && (
              <div className="mt-2 text-sm">
                <p>Verification Scores:</p>
                <ul className="list-disc list-inside mt-1">
                  <li>College: {(verificationScores.college * 100).toFixed(1)}%</li>
                  <li>Name: {(verificationScores.name * 100).toFixed(1)}%</li>
                  <li>USN: {(verificationScores.usn * 100).toFixed(1)}%</li>
                </ul>
                <p className="mt-2 text-xs">
                  Required: College ≥75%, Name ≥75%, USN ≥90%
                </p>
              </div>
            )}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">
              College
            </label>
            <select
              name="college_name"
              required
              value={formData.college_name}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
            >
              <option value="">Select your college</option>
              {colleges.map((college) => (
                <option key={college.public_id || college.college_code} value={college.college_name}>
                  {college.college_name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-slate-500 dark:text-gray-400">
              Select your college from the list above
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">
              Student Name
            </label>
            <input
              type="text"
              name="student_name"
              required
              value={formData.student_name}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
              placeholder="Enter your name as shown on ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">
              USN / Student ID
            </label>
            <input
              type="text"
              name="usn"
              required
              value={formData.usn}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 dark:focus:ring-sky-400 focus:border-blue-500 dark:focus:border-sky-400 bg-white dark:bg-slate-700 text-slate-800 dark:text-gray-200"
              placeholder="Enter your USN/Student ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">
              College ID Image
            </label>
            <div className="mt-1">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="block w-full text-sm text-slate-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-slate-700 file:text-blue-700 dark:file:text-sky-300 hover:file:bg-blue-100 dark:hover:file:bg-slate-600"
              />
              <p className="mt-1 text-xs text-slate-500 dark:text-gray-400">
                Upload a clear image of your college ID (Max 5MB)
              </p>
            </div>
            {preview && (
              <div className="mt-4">
                <img
                  src={preview}
                  alt="ID Preview"
                  className="max-w-full h-auto rounded-md border border-slate-300 dark:border-slate-600"
                />
              </div>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 dark:bg-sky-400 hover:bg-blue-700 dark:hover:bg-sky-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-sky-400 disabled:opacity-50"
            >
              {loading ? "Verifying..." : "Verify Student ID"}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate("/auth")}
              className="text-blue-600 dark:text-sky-400 hover:text-blue-500 dark:hover:text-sky-300"
            >
              Back to Login/Register
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StudentVerification;

