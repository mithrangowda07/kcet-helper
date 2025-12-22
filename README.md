# KCET EduGuide

A comprehensive rank-based college and branch recommendation platform for KCET students, featuring real reviews, meeting scheduling with Google Meet integration, and personalized counseling choices.

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Database**: MySQL
- **Authentication**: JWT (access + refresh tokens)
- **Charts**: Recharts
- **Meeting Integration**: Google Calendar API with Google Meet

## Project Structure

```
kcet-helper/
├── backend/                 # Django backend
│   ├── kcet_eduguide/       # Main Django project
│   ├── colleges/            # College, branch, cutoff models & APIs
│   ├── students/            # Student model, authentication
│   ├── reviews/             # College review system
│   ├── meetings/            # Meeting management with Google Calendar
│   └── counselling/         # Counselling choices & recommendations
├── frontend/                # React frontend
│   └── src/
│       ├── components/      # Reusable components
│       ├── pages/           # Page components
│       ├── contexts/        # React contexts (Auth)
│       ├── services/        # API service layer
│       └── types/           # TypeScript types
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Google Cloud Project with Calendar API enabled

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

   DB_NAME=kcet_eduguide
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Create MySQL database:**
   ```sql
   CREATE DATABASE kcet_eduguide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser (optional, for admin panel):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server:**
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

   Frontend will be available at `http://localhost:3000`

### Google Calendar API Setup

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

4. **Update `.env` file:**
   ```env
   GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/service-account-credentials.json
   GOOGLE_CALENDAR_EMAIL=your-calendar-email@example.com
   ```

## Database Schema

The project uses the following main tables:

- `college` - College information
- `cluster` - Cluster codes and names
- `branch` - Branch information (linked to college and cluster)
- `cutoff` - Historical cutoff data by year, round, and category
- `student` - Student accounts (both counselling and studying)
- `student_counter` - Counter for generating student IDs
- `college_reviews` - Reviews submitted by studying students
- `counselling_choices` - Saved choices by counselling students
- `student_meetings` - Meeting requests and scheduled meetings

## User Roles

### Counselling Students
- Register with KCET rank and category selection
- Get rank-based recommendations
- Save counseling choices in a table format with cutoff information
- Reorder choices via drag-and-drop with save functionality
- Search colleges and branches
- Request meetings with studying students
- View cutoff trends and reviews (defaults to their category)

### Studying Students
- Register with college and branch information
- Submit or edit detailed reviews for their branch (one review per branch)
- Accept/reject meeting requests
- View scheduled meetings with Google Meet links
- Update profile including category selection

## Features

1. **Rank-Based Recommendations**: Personalized suggestions based on KCET rank and historical cutoffs
2. **Cutoff Trends Visualization**: Interactive charts showing cutoff trends over years and rounds (defaults to user's category if logged in)
3. **Review System**: Comprehensive rating system across 10 categories (one review per branch per user)
4. **Meeting Integration**: Automatic Google Calendar event creation with Google Meet links
5. **Choice Management**: Save and organize preferred college-branch combinations with drag-and-drop reordering
6. **Search Functionality**: Search by college name, code, branch, or location
7. **Category Selection**: Users can select their category during registration from available categories
8. **Personal List Table**: Counselling students can view their choices in a table format with cutoff information
9. **Review Editing**: Studying students can edit their existing reviews instead of creating duplicates

## Deployment

### Backend (Render/Railway)
1. Set environment variables in platform dashboard
2. Configure build command: `pip install -r requirements.txt`
3. Configure start command: `gunicorn kcet_eduguide.wsgi:application`
4. Set database connection string

### Frontend (Vercel)
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable: `VITE_API_BASE_URL`

### Database (PlanetScale/MySQL Cloud)
1. Create database instance
2. Update `DB_HOST`, `DB_USER`, `DB_PASSWORD` in backend `.env`
3. Run migrations on production database

## Notes

- Student ID generation follows specific patterns:
  - Counselling: `YYYYNNNNNN` (e.g., 2025000001)
  - Studying: `<college_code>NNNNNN` (e.g., E001000001)
- Cutoff data is admin-only (entered via Django admin)
- Google Calendar integration requires service account with calendar access
- JWT tokens are stored in localStorage (consider httpOnly cookies for production)
- Category selection is required for counselling students during registration
- Reviews are limited to one per branch per user (existing reviews can be edited)
- Cutoff information in personal list uses user's category with fallback to GM category
- Review table columns are widened and text is aligned left and top for better readability

## License

This project is created for educational purposes.
