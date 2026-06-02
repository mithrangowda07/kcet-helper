# Student ID Card & Approval Migration

## Run Django migration

```bash
cd backend
python manage.py migrate students
```

## Manual MySQL (if needed)

```sql
ALTER TABLE student
  ADD COLUMN id_card_url VARCHAR(1000) NULL,
  ADD COLUMN approval_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  ADD COLUMN reviewed_at DATETIME NULL,
  ADD COLUMN rejection_reason TEXT NOT NULL DEFAULT '',
  ADD COLUMN reviewed_by_id BIGINT NULL,
  ADD CONSTRAINT fk_student_reviewed_by
    FOREIGN KEY (reviewed_by_id) REFERENCES admin_account(id);

ALTER TABLE student DROP COLUMN id_card_image;

UPDATE student SET approval_status = 'APPROVED' WHERE type_of_student = 'counselling';
UPDATE student SET approval_status = 'APPROVED'
  WHERE type_of_student = 'studying' AND is_verified_student = 1;
```

## SMTP (.env)

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=you@example.com
```

Uses the same S3 bucket as branch insights (`AWS_STORAGE_BUCKET_NAME`). ID cards are stored under `student-id-cards/`.
