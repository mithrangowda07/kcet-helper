# KCET EduGuide - Setup & Configuration Guide

This guide will walk you through setting up and running the KCET EduGuide project from scratch.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **MySQL 8.0 or higher** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **Git** (optional, for cloning) - [Download Git](https://git-scm.com/)

## 🔧 Step-by-Step Setup

### Step 1: Database Setup

1. **Start MySQL Server**
   ```bash
   # On Windows (if installed as service, it should start automatically)
   # On Linux/Mac:
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Login to MySQL**
   ```bash
   mysql -u root -p
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE kcet_eduguide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

### Step 2: Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create Python virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file in `backend/` directory**
   
   Create a new file named `.env` in the `backend` folder with the following content:
   
   ```env
   # Django Settings
   SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Configuration
   DB_NAME=kcet_eduguide
   DB_USER=root
   DB_PASSWORD=your_mysql_password_here
   DB_HOST=localhost
   DB_PORT=3306

   # Google Calendar API (Optional - can be set later)
   GOOGLE_CALENDAR_CREDENTIALS_PATH=
   GOOGLE_CALENDAR_EMAIL=
   ```

   **⚠️ IMPORTANT: Replace the following values:**
   - `SECRET_KEY`: Generate a random secret key (you can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DB_PASSWORD`: Your MySQL root password (or the password for the user you'll use)

5. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser (Optional - for Django Admin)**
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create admin account
   ```

7. **Start Django Development Server**
   ```bash
   python manage.py runserver
   ```

   The backend should now be running at `http://localhost:8000`

   **Test it:** Open `http://localhost:8000/admin/` in your browser (if you created a superuser)

### Step 3: Frontend Setup

1. **Open a NEW terminal window** (keep backend running)

2. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Create `.env` file in `frontend/` directory (Optional)**
   
   Create a new file named `.env` in the `frontend` folder:
   
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```
   
   **Note:** If you don't create this file, the frontend will use `http://localhost:8000/api` by default (configured in `vite.config.ts`)

5. **Start Frontend Development Server**
   ```bash
   npm run dev
   ```

   The frontend should now be running at `http://localhost:3000`

### Step 4: Verify Installation

1. **Open your browser** and go to `http://localhost:3000`
2. You should see the landing page
3. Try registering a new account:
   - Click "Login / Register"
   - Choose "Counselling Student" or "Studying Student"
   - Fill in the registration form
   - Submit

## 🔑 Configuration Changes Required

### 1. Database Configuration (MUST CHANGE)

**File:** `backend/.env`

```env
DB_PASSWORD=your_actual_mysql_password
```

If you're using a different MySQL user (not root):
```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
```

### 2. Django Secret Key (MUST CHANGE)

**File:** `backend/.env`

Generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it in `.env`:
```env
SECRET_KEY=<paste-generated-key-here>
```

### 3. Google Calendar API (OPTIONAL - for meeting features)

If you want to enable Google Meet integration:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** (or select existing)
3. **Enable Google Calendar API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in name (e.g., "kcet-eduguide")
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
5. **Create Key:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file
6. **Share Calendar:**
   - Open the downloaded JSON file
   - Copy the `client_email` value (e.g., `kcet-eduguide@project-id.iam.gserviceaccount.com`)
   - Go to [Google Calendar](https://calendar.google.com/)
   - Click the "+" next to "Other calendars" > "Create new calendar"
   - Or use your existing calendar
   - Click on the calendar > "Settings and sharing"
   - Under "Share with specific people", click "Add people"
   - Paste the `client_email` from the JSON file
   - Give "Make changes to events" permission
   - Click "Send"
7. **Update `.env` file:**
   ```env
   GOOGLE_CALENDAR_CREDENTIALS_PATH=C:\path\to\credentials.json
   GOOGLE_CALENDAR_EMAIL=your-email@gmail.com
   ```
   
   **Note:** Use absolute path for `GOOGLE_CALENDAR_CREDENTIALS_PATH`

### 4. CORS Settings (If needed)

**File:** `backend/kcet_eduguide/settings.py`

If your frontend runs on a different port, add it to `CORS_ALLOWED_ORIGINS`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:3000",
]
```

### 5. Allowed Hosts (For Production)

**File:** `backend/.env`

When deploying, update:
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 📝 Initial Data Setup

### Adding Colleges and Branches

You can add data in two ways:

**Option 1: Django Admin (Recommended)**
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Add:
   - Clusters (e.g., "A", "B", "C")
   - Colleges
   - Branches
   - Cutoff data

**Option 2: SQL Scripts**
Create SQL INSERT statements or use Django management commands.

### Sample Data Structure

1. **Cluster:**
   - cluster_code: "A"
   - cluster_name: "Cluster A"

2. **College:**
   - college_id: "001"
   - college_code: "RVU"
   - college_name: "RV University"
   - location: "Bangalore"

3. **Branch:**
   - unique_key: "001A01" (college_id + cluster_code + branch_id)
   - college_id: "001"
   - cluster_id: "A"
   - branch_id: "01"
   - branch_name: "Computer Science Engineering"

4. **Cutoff:**
   - unique_key: "001A01"
   - category: "GM"
   - cutoff_2025_r1: "1000"
   - cutoff_2025_r2: "1200"
   - (etc.)

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

## 🐛 Troubleshooting

### Backend Issues

**Issue: `mysqlclient` installation fails**
```bash
# Windows - Install MySQL Connector/C first, then:
pip install mysqlclient

# Linux
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient

# Mac
brew install mysql
pip install mysqlclient
```

**Issue: Database connection error**
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in `.env` file
- Ensure database exists: `SHOW DATABASES;`

**Issue: Migration errors**
```bash
python manage.py makemigrations --empty <app_name>
python manage.py migrate
```

### Frontend Issues

**Issue: `npm install` fails**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Issue: API calls fail (CORS error)**
- Check backend is running
- Verify `CORS_ALLOWED_ORIGINS` in `settings.py`
- Check browser console for exact error

**Issue: Port 3000 already in use**
```bash
# Use different port
npm run dev -- --port 3001
```

### Google Calendar Issues

**Issue: "Credentials file not found"**
- Verify absolute path in `.env`
- On Windows, use forward slashes or double backslashes: `C:/path/to/file.json` or `C:\\path\\to\\file.json`

**Issue: "Permission denied"**
- Ensure calendar is shared with service account email
- Check service account has "Make changes to events" permission

## 📦 Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use production database (not local MySQL)
- [ ] Set up proper CORS origins
- [ ] Configure static files serving
- [ ] Set up SSL/HTTPS
- [ ] Use environment variables for all secrets
- [ ] Set up proper logging
- [ ] Configure backup strategy for database

## 🆘 Need Help?

If you encounter issues:

1. Check error messages in terminal/console
2. Verify all environment variables are set correctly
3. Ensure all services (MySQL, backend, frontend) are running
4. Check browser console for frontend errors
5. Review Django logs for backend errors

## 📚 Next Steps

After setup:

1. **Add initial data** via Django admin
2. **Test registration** for both user types
3. **Add cutoff data** for branches
4. **Configure Google Calendar** (if using meeting features)
5. **Test all features:**
   - Recommendations
   - Reviews
   - Meetings
   - Search

---

**Happy Coding! 🎓**

