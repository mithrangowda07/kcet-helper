# Branch Insights (S3 + Admin Panel)

Branch insights are stored in **AWS S3** and managed through the React admin UI at `/admin/login`.

## 1. Install backend dependencies

```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 2. Configure environment

Copy `backend/.env.example` to `backend/.env` and set:

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
AWS_S3_REGION_NAME=ap-south-1
```

## 3. Connect to AWS S3

### Create a bucket

1. Open [AWS S3 Console](https://s3.console.aws.amazon.com/s3/).
2. **Create bucket** (e.g. `kcet-eduguide-insights`).
3. Pick the same region as `AWS_S3_REGION_NAME` (e.g. `ap-south-1`).

### IAM user (recommended)

1. IAM → **Users** → **Create user** (programmatic access).
2. Attach a policy with at least:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/branch-insights/*"
    }
  ]
}
```

3. Copy **Access key ID** and **Secret access key** into `.env`.

### Object layout

Uploaded files are stored as:

```text
branch-insights/{college_code}/{branch_id}/insight.json
```

Example: `branch-insights/RVCE/01/insight.json`  
(`branch_id` is the 2-character branch code from the database.)

The bucket can stay **private**; the Django API fetches JSON with boto3 and returns it to the frontend.

Optional public reads: set bucket policy or `AWS_S3_DEFAULT_ACL=public-read` (not required for the app flow).

### Verify credentials

```bash
cd backend
python -c "
import boto3, os
from dotenv import load_dotenv
load_dotenv()
client = boto3.client('s3',
    region_name=os.getenv('AWS_S3_REGION_NAME'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
print('Buckets:', [b['Name'] for b in client.list_buckets()['Buckets']])
"
```

## 4. Database migration

```bash
cd backend
python manage.py makemigrations insights_manager
python manage.py migrate
```

## 5. Create a platform admin

**Recommended (Django command):**

```bash
python manage.py create_platform_admin --email admin@example.com --password 'YourSecurePassword123' --name 'Insights Admin'
```

**MySQL (manual)** — passwords must be Django-hashed; prefer the command above.

If you must insert via SQL, generate a hash first:

```bash
python manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('YourSecurePassword123'))"
```

Then:

```sql
INSERT INTO admin_account (email, password, name, is_active, created_at)
VALUES (
  'admin@example.com',
  'pbkdf2_sha256$...paste hash from shell...',
  'Insights Admin',
  1,
  UTC_TIMESTAMP()
);
```

## 6. Run the app

```bash
# Backend
cd backend && python manage.py runserver

# Frontend
cd frontend && npm run dev
```

- Admin UI: http://localhost:3000/admin/login  
- Upload insights, then open any branch page → **Branch Insights**

## API summary

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/admin/login/` | Public |
| GET | `/api/admin/colleges/` | Admin JWT |
| GET | `/api/admin/colleges/{college_id}/branches/` | Admin JWT |
| POST | `/api/admin/branch-insights/upload/` | Admin JWT |
| GET | `/api/branch-insights/{unique_key}/` | Public |

## JSON schema

Upload a **single object** or a **one-element array** matching `backend/about_branch.json` (sample reference). Required fields:

- `college_name`, `branch_name` (must match selected college/branch)
- `about`, `admission_cutoffs`, `placements`, `one_line_summary` (strings)
- `pros_cons.pros[]`, `pros_cons.cons[]`
- `features[]`, `additional_info[]`

## Migrate existing local JSON

Use the admin UI to upload entries from `backend/about_branch.json` per college/branch, or script uploads via the admin API.
