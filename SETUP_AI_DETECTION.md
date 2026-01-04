# AI Detection System Setup Guide

This guide explains how to set up and run the new AI vs Human text detection system for reviews.

## 📋 Overview

The system uses a pre-trained ML model to detect AI-generated text in review submissions. Each review field is checked independently, and submissions are blocked if any field contains AI-generated content.

## 🔧 Setup Instructions

### Step 1: Place Your ML Model Files

1. Ensure the model directory exists:
   ```bash
   mkdir -p backend/reviews/ml_models
   ```

2. Place your trained model files in `backend/reviews/ml_models/`:
   - `tfidf_vectorizer.pkl` - The TF-IDF vectorizer used during training
   - `review_ai_detector.pkl` - The trained classification model

   **Important:** These files must be named exactly as shown above.

### Step 2: Install Python Dependencies

The required dependencies are already in `requirements.txt`:
- `scikit-learn==1.3.2` - For ML model loading and prediction
- `joblib==1.3.2` - For loading .pkl files

Install them:
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Verify Model Loading

1. Start your Django server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Check the server logs. You should see:
   ```
   ML model and vectorizer loaded successfully at startup
   ```

   If you see an error, verify:
   - Model files are in `backend/reviews/ml_models/`
   - Files are named correctly (`tfidf_vectorizer.pkl` and `review_ai_detector.pkl`)
   - Files are valid pickle files

### Step 4: Start Frontend (if not already running)

```bash
cd frontend
npm install  # if first time
npm run dev
```

## 🚀 How to Run

### Backend

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Activate your virtual environment (if using one):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Start Django server:
   ```bash
   python manage.py runserver
   ```

   The server will start on `http://localhost:8000`

### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if first time):
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:5173` (or the port shown)

## 🧪 Testing the API Endpoints

### Test Single Field Check:

```bash
curl -X POST http://localhost:8000/api/reviews/check-text/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "teaching_review",
    "text": "The teaching quality at RVCE is strong..."
  }'
```

Expected response:
```json
{
  "field": "teaching_review",
  "label": "HUMAN-WRITTEN",
  "ai_probability": 0.23
}
```

### Test Batch Validation:

```bash
curl -X POST http://localhost:8000/api/reviews/validate-all/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": {
      "teaching_review": "The teaching quality is excellent...",
      "courses_review": "The curriculum is well-structured...",
      "library_review": "The library has a good collection...",
      "research_review": "Research opportunities are available..."
    }
  }'
```

Expected response:
```json
{
  "results": {
    "teaching_review": "HUMAN-WRITTEN",
    "courses_review": "HUMAN-WRITTEN",
    "library_review": "HUMAN-WRITTEN",
    "research_review": "HUMAN-WRITTEN"
  },
  "can_submit": true,
  "ai_fields": []
}
```

## 📝 Features

### Backend Features

1. **Model Loading**: Models are loaded once at server startup (singleton pattern)
2. **Per-Field Validation**: Each review field is checked independently
3. **Strict Enforcement**: Backend blocks submission if ANY field is AI-generated
4. **Rate Limiting**: 10 requests per minute per user for text checking
5. **Exact Logic**: Uses the exact cleaning, threshold (0.7), and prediction logic from your working model

### Frontend Features

1. **Per-Field Checking**: Each textarea has a "Check Text" button
2. **Real-Time Feedback**: Shows status badges (✅ HUMAN-WRITTEN or ❌ AI-GENERATED)
3. **Auto-Check**: Automatically checks text 1.5 seconds after user stops typing
4. **Submit Blocking**: Submit button is disabled if:
   - Any field is AI-GENERATED
   - Any field with text is unchecked
5. **Validation Summary**: Shows summary of all fields before submission
6. **Confidence Display**: Shows AI probability percentage

## 🔒 Security & Performance

- **Max text length**: 1000 characters (truncated if longer)
- **Rate limiting**: 10 checks per minute per user
- **Backend enforcement**: Even if frontend is bypassed, backend rejects AI-generated content
- **Fail-closed**: If model fails to load, submissions are blocked (not allowed)

## ⚠️ Important Notes

1. **Model Files**: The system expects `tfidf_vectorizer.pkl` and `review_ai_detector.pkl` (NOT `vectorizer.pkl` and `model.pkl`)

2. **Threshold**: The threshold is fixed at 0.7 (probability_ai > 0.7 = AI-GENERATED). Do NOT modify this.

3. **Cleaning Logic**: The text cleaning uses exact logic from your working model. Do NOT modify `clean_text()` function.

4. **Empty Text**: Empty text fields are considered HUMAN-WRITTEN (no AI detection needed).

5. **Model Loading**: Models are loaded once at startup. If you change model files, restart the Django server.

## 🐛 Troubleshooting

### Model Not Loading

- Check that files exist in `backend/reviews/ml_models/`
- Verify file names are exactly: `tfidf_vectorizer.pkl` and `review_ai_detector.pkl`
- Check Django server logs for specific error messages
- Ensure joblib and scikit-learn are installed correctly

### API Returns 503 (Service Unavailable)

- Model failed to load at startup
- Check server logs for error details
- Verify model files are valid pickle files

### Frontend Shows "Unchecked" After Checking

- Check browser console for errors
- Verify API endpoint is accessible
- Check that authentication token is valid
- Verify backend is running and model is loaded

## 📚 API Documentation

### POST /api/reviews/check-text/

Check a single text field.

**Request:**
```json
{
  "field": "teaching_review",
  "text": "The teaching quality is excellent..."
}
```

**Response:**
```json
{
  "field": "teaching_review",
  "label": "HUMAN-WRITTEN",
  "ai_probability": 0.23
}
```

### POST /api/reviews/validate-all/

Validate all review fields in batch.

**Request:**
```json
{
  "reviews": {
    "teaching_review": "...",
    "courses_review": "...",
    ...
  }
}
```

**Response:**
```json
{
  "results": {
    "teaching_review": "HUMAN-WRITTEN",
    "courses_review": "AI-GENERATED",
    ...
  },
  "can_submit": false,
  "ai_fields": ["courses_review"]
}
```

### POST /api/reviews/

Create or update a review (automatically validates all fields).

**Response (if AI detected):**
```json
{
  "error": "Review submission rejected: AI-generated content detected",
  "message": "The following review fields contain AI-generated text: Course Curriculum",
  "ai_fields": ["courses_review"],
  "field_display_names": ["Course Curriculum"],
  "validation_results": {...}
}
```

## ✅ Checklist

- [ ] Model files placed in `backend/reviews/ml_models/`
- [ ] Files named correctly: `tfidf_vectorizer.pkl` and `review_ai_detector.pkl`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Django server starts without errors
- [ ] Model loads successfully (check logs)
- [ ] Frontend can connect to backend
- [ ] "Check Text" button works for each field
- [ ] Status badges display correctly
- [ ] Submit button blocks when AI is detected
- [ ] Backend rejects AI-generated submissions

## 🎯 Next Steps

1. Place your model files in the correct directory
2. Start the backend server
3. Start the frontend server
4. Test the review submission flow
5. Verify AI detection is working correctly

For issues or questions, check the server logs and browser console for error messages.

