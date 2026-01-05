# KCET EduGuide

A comprehensive rank-based college and branch recommendation platform for KCET students, featuring real reviews, meeting scheduling with Google Meet integration, AI-powered review validation, and personalized counseling choices.

## 🚀 Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **Frontend**: React 18 + TypeScript + Vite 5
- **Styling**: Tailwind CSS 3.3.6
- **Database**: MySQL 8.0+
- **Authentication**: JWT (SimpleJWT with access + refresh tokens)
- **Charts**: Recharts 2.10.3
- **Meeting Integration**: Google Calendar API with Google Meet
- **OCR & Verification**: Tesseract OCR + OpenCV + RapidFuzz
- **AI Detection**: scikit-learn 1.8.0 (ML model for review validation)

## 📁 Project Structure

```
kcet-helper/
├── backend/                 # Django backend
│   ├── kcet_eduguide/       # Main Django project
│   ├── colleges/            # College, branch, cutoff models & APIs
│   ├── students/            # Student model, authentication, verification
│   ├── reviews/             # College review system with AI detection
│   ├── meetings/            # Meeting management with Google Calendar
│   └── counselling/         # Counselling choices & recommendations
├── frontend/                # React frontend
│   └── src/
│       ├── components/      # Reusable components (Navbar, ProtectedRoute, etc.)
│       ├── pages/           # Page components
│       ├── contexts/        # React contexts (Auth, Theme)
│       ├── services/        # API service layer
│       └── types/           # TypeScript type definitions
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- **Python**: 3.9+ (3.11 recommended)
- **Node.js**: 18+ (20+ recommended)
- **MySQL**: 8.0+
- **Tesseract OCR**: Required for student verification
  - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
- **Google Cloud Project**: With Calendar API enabled (for meeting features)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file in backend directory:**
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Configuration
   DB_NAME=kcet_eduguide
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_HOST=localhost
   DB_PORT=3306

   # Google Calendar API (Optional - for meeting features)
   GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/service-account-credentials.json
   GOOGLE_CALENDAR_EMAIL=your-calendar-email@example.com

   # Tesseract OCR Path (Windows only)
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

5. **Create MySQL database:**
   ```sql
   CREATE DATABASE kcet_eduguide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional, for admin panel):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Place ML model files (for AI review detection):**
   - Copy `tfidf_vectorizer.pkl` to `backend/reviews/ml_models/`
   - Copy `review_ai_detector.pkl` to `backend/reviews/ml_models/`
   - These files are required for AI-powered review validation

9. **Run development server:**
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file in frontend directory (optional):**
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173` (Vite default port)

### Google Calendar API Setup (Optional)

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Calendar API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
   - Download JSON key file
   - Share calendar with service account email

4. **Update `.env` file:**
   ```env
   GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/service-account-credentials.json
   GOOGLE_CALENDAR_EMAIL=your-calendar-email@example.com
   ```

## 📊 Database Schema

The project uses the following main tables:

- `college` - College information (name, code, location)
- `cluster` - Cluster codes and names
- `branch` - Branch information (linked to college and cluster)
- `cutoff` - Historical cutoff data by year, round, and category
- `student` - Student accounts (both counselling and studying)
  - Includes `id_card_image` (LONGBLOB) for studying students
- `student_counter` - Counter for generating student IDs
- `student_verification` - Verification records for audit trail
- `college_reviews` - Reviews submitted by studying students
- `counselling_choices` - Saved choices by counselling students
- `student_meetings` - Meeting requests and scheduled meetings

## 👥 User Roles & Registration

### Registration Flow

The system supports **two separate registration flows**:

1. **Counselling Student Registration** (`/register/counselling`)
   - Simple registration form
   - Requires: Name, Email, Phone, Password, KCET Rank, Category (optional)
   - No verification required
   - Auto-verified upon registration

2. **Studying Student Registration** (`/register/studying`)
   - Registration with integrated ID card verification
   - Requires: Name, Email, Phone, Password, College, Branch, Year of Starting, USN, Category (optional), ID Card Image
   - **Verification happens FIRST** before account creation
   - Uses OCR (Tesseract) to extract text from ID card
   - Fuzzy matching validates: College name (≥75%), Student name (≥75%), USN (≥90%) or Email domain (≥80%)
   - If verification fails: No account created, no image stored
   - If verification passes: Account created with image stored as binary (LONGBLOB)
   - All operations in atomic transaction (rollback on failure)

### Counselling Students

**Features:**
- Register with KCET rank and category selection
- Get rank-based recommendations
- Save counseling choices in a table format with cutoff information
- Reorder choices via drag-and-drop with save functionality
- Search colleges and branches
- Request meetings with studying students
- View cutoff trends and reviews (defaults to their category)
- Export choices to PDF

### Studying Students

**Features:**
- Register with college and branch information (with ID verification)
- Submit or edit detailed reviews for their branch (one review per branch)
- Reviews validated by AI model to detect AI-generated content
- Accept/reject meeting requests
- View scheduled meetings with Google Meet links
- Update profile including category selection

## ✨ Features

### 1. **Dual Registration System**
   - Separate registration flows for counselling and studying students
   - Role selection page for choosing registration type
   - Integrated verification for studying students

### 2. **Student Verification System**
   - OCR-based ID card verification using Tesseract
   - Fuzzy matching algorithm for text validation
   - Image stored as binary in database (LONGBLOB)
   - Atomic transaction ensures data integrity

### 3. **AI-Powered Review Validation**
   - ML model detects AI-generated review content
   - Uses TF-IDF vectorization and logistic regression
   - Validates all review fields before submission
   - Prevents AI-generated reviews from being posted

### 4. **Rank-Based Recommendations**
   - Personalized suggestions based on KCET rank and historical cutoffs
   - Considers user's category and rank
   - Shows probability of admission

### 5. **Cutoff Trends Visualization**
   - Interactive charts showing cutoff trends over years and rounds
   - Defaults to user's category if logged in
   - Supports multiple categories and rounds

### 6. **Review System**
   - Comprehensive rating system across 10 categories:
     - Teaching Quality
     - Course Curriculum
     - Library Facilities
     - Research Opportunities
     - Internship Support
     - Infrastructure
     - Administration
     - Extracurricular Activities
     - Safety & Security
     - Placement Support
   - One review per branch per user (existing reviews can be edited)
   - AI validation prevents fake/AI-generated reviews

### 7. **Meeting Integration**
   - Automatic Google Calendar event creation with Google Meet links
   - Request/accept/reject meeting functionality
   - Email notifications (if configured)
   - Meeting status tracking

### 8. **Choice Management**
   - Save and organize preferred college-branch combinations
   - Drag-and-drop reordering with save functionality
   - Table view with cutoff information
   - Export to PDF functionality

### 9. **Search Functionality**
   - Search by college name, code, branch, or location
   - Filter by location
   - Real-time search results

### 10. **Theme Support**
   - Light and dark theme support
   - Theme preference saved in localStorage
   - Automatic system theme detection

## 🔐 Authentication & Security

- **JWT Authentication**: Access and refresh tokens
- **Password Requirements**: 
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- **Email Uniqueness**: Enforced at database level
- **USN Uniqueness**: Enforced for studying students
- **Image Validation**: MIME type and size validation (max 10MB)
- **Atomic Transactions**: Ensures data integrity for studying student registration

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/counselling/` - Register counselling student
- `POST /api/auth/register/studying/` - Register studying student (with verification)
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user
- `PATCH /api/auth/profile/` - Update profile

### Colleges & Branches
- `GET /api/colleges/` - List all colleges
- `GET /api/colleges/{publicId}/` - College details
- `GET /api/branches/by-code/{code}/` - Get branches by college code
- `GET /api/branches/{publicId}/` - Branch details

### Reviews
- `POST /api/reviews/validate-all/` - Validate all review fields (AI detection)
- `POST /api/reviews/` - Create/update review
- `GET /api/reviews/my-review/{uniqueKey}/` - Get user's review
- `GET /api/reviews/branch/{publicId}/` - Get all reviews for branch

### Meetings
- `GET /api/meetings/my-invitations/` - Get meeting invitations
- `POST /api/meetings/request/` - Request a meeting
- `POST /api/meetings/{id}/accept/` - Accept meeting
- `POST /api/meetings/{id}/reject/` - Reject meeting

### Counselling
- `GET /api/counselling/choices/` - Get saved choices
- `POST /api/counselling/choices/` - Save choice
- `PUT /api/counselling/choices/{id}/` - Update choice
- `DELETE /api/counselling/choices/{id}/` - Delete choice
- `POST /api/counselling/reorder/` - Reorder choices

## 🚀 Deployment

### Backend (Render/Railway/Heroku)

1. **Set environment variables:**
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.com`
   - Database connection variables
   - Google Calendar credentials (if using meetings)

2. **Configure build command:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure start command:**
   ```bash
   gunicorn kcet_eduguide.wsgi:application
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Frontend (Vercel/Netlify)

1. **Connect GitHub repository**

2. **Set build command:**
   ```bash
   npm run build
   ```

3. **Set output directory:**
   ```
   dist
   ```

4. **Add environment variable:**
   ```
   VITE_API_BASE_URL=https://your-backend-api.com/api
   ```

### Database (PlanetScale/MySQL Cloud)

1. Create database instance
2. Update `DB_HOST`, `DB_USER`, `DB_PASSWORD` in backend `.env`
3. Run migrations on production database:
   ```bash
   python manage.py migrate
   ```

## 📝 Important Notes

### Student ID Generation
- **Counselling**: `YYYYNNNNNN` (e.g., 2025000001)
- **Studying**: `<college_code>NNNNNN` (e.g., E005000001)

### Image Storage
- ID card images stored as binary (LONGBLOB) in MySQL database
- No file system storage for images
- Images not returned in API responses (privacy)

### Verification Rules
- College name match: ≥75%
- Student name match: ≥75%
- USN match: ≥90% OR Email domain match: ≥80%
- All checks must pass for verification to succeed

### AI Review Detection
- Model trained with scikit-learn 1.8.0
- Requires `tfidf_vectorizer.pkl` and `review_ai_detector.pkl` in `backend/reviews/ml_models/`
- Validates all review text fields before submission
- Threshold: 0.7 (70% probability = AI-generated)

### Data Entry
- Cutoff data is admin-only (entered via Django admin)
- College and branch data managed through Django admin
- Categories loaded from database with fallback to hardcoded list

### Security Considerations
- JWT tokens stored in localStorage (consider httpOnly cookies for production)
- Password hashing handled by Django's AbstractBaseUser
- Email normalization (lowercase) for consistency
- Race condition protection for email/USN uniqueness
- Atomic transactions for critical operations

## 🐛 Troubleshooting

### Tesseract OCR Issues
- **Windows**: Ensure Tesseract is installed and path is correct in settings
- **Linux/Mac**: Verify Tesseract is in PATH
- Check logs for OCR extraction errors

### ML Model Loading Issues
- Ensure model files are in `backend/reviews/ml_models/`
- Check scikit-learn version matches (1.8.0)
- Verify model files are not corrupted

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database exists and user has permissions

### Migration Issues
- Run `python manage.py makemigrations` if new models added
- Run `python manage.py migrate` to apply migrations
- Check for migration conflicts

## 📄 License

This project is created for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues and questions, please open an issue on GitHub.
