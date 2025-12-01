# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Database
```bash
mysql -u root -p
CREATE DATABASE kcet_eduguide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Create .env file (see below)
python manage.py migrate
python manage.py runserver
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## ⚙️ Required Configuration Files

### `backend/.env` (CREATE THIS FILE)
```env
SECRET_KEY=django-insecure-change-this-to-random-key-min-50-chars
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=kcet_eduguide
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_HOST=localhost
DB_PORT=3306

GOOGLE_CALENDAR_CREDENTIALS_PATH=
GOOGLE_CALENDAR_EMAIL=
```

### `frontend/.env` (OPTIONAL)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## ✅ What You MUST Change

1. **`backend/.env` → `DB_PASSWORD`**: Your MySQL password
2. **`backend/.env` → `SECRET_KEY`**: Generate with:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

## 🎯 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## 📝 First Steps After Setup

1. Create superuser: `python manage.py createsuperuser`
2. Login to admin: http://localhost:8000/admin
3. Add data: Clusters → Colleges → Branches → Cutoffs
4. Test registration at http://localhost:3000

---

For detailed instructions, see `SETUP_GUIDE.md`

