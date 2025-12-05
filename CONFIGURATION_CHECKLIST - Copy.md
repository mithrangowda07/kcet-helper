# Configuration Checklist

Use this checklist to ensure all required configurations are completed.

## ✅ Required Configurations

### 1. Backend Environment File (`backend/.env`)

- [ ] **SECRET_KEY** - Generated random Django secret key
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **DB_PASSWORD** - Your MySQL root password (or custom user password)

- [ ] **DB_USER** - MySQL username (default: `root`)

- [ ] **DB_NAME** - Database name (default: `kcet_eduguide`)

- [ ] **DB_HOST** - MySQL host (default: `localhost`)

- [ ] **DB_PORT** - MySQL port (default: `3306`)

### 2. Database Setup

- [ ] MySQL server is running
- [ ] Database `kcet_eduguide` is created
- [ ] Database user has proper permissions

### 3. Python Dependencies

- [ ] Virtual environment created and activated
- [ ] All packages from `requirements.txt` installed
- [ ] `mysqlclient` installed successfully (may need system dependencies)

### 4. Django Migrations

- [ ] Migrations created: `python manage.py makemigrations`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Superuser created (optional): `python manage.py createsuperuser`

### 5. Frontend Environment File (`frontend/.env`) - Optional

- [ ] **VITE_API_BASE_URL** - Backend API URL (default: `http://localhost:8000/api`)

### 6. Node.js Dependencies

- [ ] All packages from `package.json` installed
- [ ] No installation errors

## 🔧 Optional Configurations

### Google Calendar API (For Meeting Features)

- [ ] Google Cloud Project created
- [ ] Google Calendar API enabled
- [ ] Service Account created
- [ ] Service Account JSON key downloaded
- [ ] Calendar shared with service account email
- [ ] **GOOGLE_CALENDAR_CREDENTIALS_PATH** set in `backend/.env`
- [ ] **GOOGLE_CALENDAR_EMAIL** set in `backend/.env`

### CORS Settings (If Frontend on Different Port)

- [ ] Updated `CORS_ALLOWED_ORIGINS` in `backend/kcet_eduguide/settings.py`

## 🚀 Running Checklist

### Backend

- [ ] Virtual environment activated
- [ ] `.env` file exists and configured
- [ ] MySQL database exists and accessible
- [ ] Migrations applied
- [ ] Server starts without errors: `python manage.py runserver`
- [ ] Can access admin panel: http://localhost:8000/admin

### Frontend

- [ ] Node modules installed
- [ ] Backend is running
- [ ] Frontend starts without errors: `npm run dev`
- [ ] Can access frontend: http://localhost:3000
- [ ] No CORS errors in browser console

## 📝 Initial Data Setup

- [ ] At least one Cluster added
- [ ] At least one College added
- [ ] At least one Branch added
- [ ] Cutoff data added (for recommendations to work)

## 🧪 Testing Checklist

- [ ] Can register as Counselling Student
- [ ] Can register as Studying Student
- [ ] Can login with registered account
- [ ] Can view dashboard
- [ ] Can search colleges
- [ ] Can view college details
- [ ] Can see recommendations (if cutoff data exists)
- [ ] Can add choices (counselling students)
- [ ] Can submit reviews (studying students)
- [ ] Can request meetings (counselling students)
- [ ] Can accept/reject meetings (studying students)

## 🐛 Common Issues to Check

- [ ] MySQL is running
- [ ] Port 8000 is not in use (backend)
- [ ] Port 3000 is not in use (frontend)
- [ ] No firewall blocking ports
- [ ] Python version is 3.9+
- [ ] Node.js version is 18+
- [ ] All environment variables are set correctly
- [ ] No typos in `.env` file values

---

**Once all items are checked, your application should be ready to use!**

