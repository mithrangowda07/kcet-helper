# API Test Examples

## Registration Endpoint

### For Counselling Student

**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
  "type_of_student": "counselling",
  "email_id": "student@example.com",
  "phone_number": "1234567890",
  "password": "password123",
  "password_confirm": "password123",
  "kcet_rank": 5000
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "type_of_student": "counselling",
    "email_id": "student@example.com",
    "phone_number": "1234567890",
    "password": "password123",
    "password_confirm": "password123",
    "kcet_rank": 5000
  }'
```

### For Studying Student

**Request Body:**
```json
{
  "type_of_student": "studying",
  "email_id": "studying@example.com",
  "phone_number": "1234567890",
  "password": "password123",
  "password_confirm": "password123",
  "college_code": "RVU",
  "unique_key": "001A01",
  "year_of_starting": 2023
}
```

**Note:** `unique_key` must exist in the `branch` table first!

## Login Endpoint

**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email_id": "student@example.com",
  "password": "password123"
}
```

## Common Validation Errors

### Missing Required Fields
```json
{
  "errors": {
    "type_of_student": ["This field is required."],
    "email_id": ["This field is required."],
    "phone_number": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

### Password Mismatch
```json
{
  "errors": {
    "password": ["Passwords do not match"]
  }
}
```

### Missing KCET Rank (Counselling)
```json
{
  "errors": {
    "kcet_rank": ["kcet_rank is required for counselling students"]
  }
}
```

### Missing College Info (Studying)
```json
{
  "errors": {
    "college_code": ["college_code is required for studying students"],
    "unique_key": ["unique_key is required for studying students"],
    "year_of_starting": ["year_of_starting is required for studying students"]
  }
}
```

### Invalid Unique Key
```json
{
  "errors": {
    "unique_key": ["Invalid pk \"XXX\" - object does not exist."]
  }
}
```

**Solution:** Make sure the branch with that `unique_key` exists in the database first!

## Testing with Postman/Thunder Client

1. Set method to `POST`
2. URL: `http://localhost:8000/api/auth/register/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Use one of the examples above
5. Check response for detailed error messages

