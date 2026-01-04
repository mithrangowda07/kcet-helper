"""
AI vs Human Text Detection - Review Checker

This module uses the EXACT working model provided by the user.
DO NOT modify the cleaning logic, threshold, or prediction logic.
"""
import joblib
import re
import os
import logging

logger = logging.getLogger(__name__)

# Global variables to store loaded model and vectorizer
_vectorizer = None
_model = None
_model_loaded = False


def load_model():
    """
    Load saved model & vectorizer (load ONCE at startup).
    
    Expected files:
    - tfidf_vectorizer.pkl: The TF-IDF vectorizer
    - review_ai_detector.pkl: The trained classification model
    
    These files should be placed in backend/reviews/ml_models/ directory
    """
    global _vectorizer, _model, _model_loaded
    
    if _model_loaded:
        logger.info("Model already loaded, skipping reload")
        return True
    
    try:
        # Get the base directory (backend/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, 'reviews', 'ml_models')
        
        vectorizer_path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')
        model_path = os.path.join(models_dir, 'review_ai_detector.pkl')
        
        # Check if files exist
        if not os.path.exists(vectorizer_path):
            logger.error(f"Vectorizer file not found at: {vectorizer_path}")
            logger.error("Please place tfidf_vectorizer.pkl in backend/reviews/ml_models/")
            return False
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at: {model_path}")
            logger.error("Please place review_ai_detector.pkl in backend/reviews/ml_models/")
            return False
        
        # Load vectorizer and model
        logger.info(f"Loading vectorizer from: {vectorizer_path}")
        _vectorizer = joblib.load(vectorizer_path)
        
        logger.info(f"Loading model from: {model_path}")
        _model = joblib.load(model_path)
        
        _model_loaded = True
        logger.info("ML model and vectorizer loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading ML model: {str(e)}", exc_info=True)
        _model_loaded = False
        return False


def clean_text(text):
    """
    Clean text using EXACT logic from working model.
    DO NOT MODIFY THIS FUNCTION.
    """
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_review(review_text):
    """
    Check if review text is AI-generated or Human-written.
    Uses EXACT logic from working model.
    DO NOT MODIFY threshold (0.7) or preprocessing.
    
    Args:
        review_text (str): The text to check
        
    Returns:
        tuple: (label, probability_ai)
            - label: "AI-GENERATED" or "HUMAN-WRITTEN"
            - probability_ai: float (0.0 to 1.0)
            
    Raises:
        RuntimeError: If model is not loaded
    """
    global _vectorizer, _model, _model_loaded
    
    if not _model_loaded or _vectorizer is None or _model is None:
        raise RuntimeError("ML model not loaded. Call load_model() first.")
    
    # Limit text length (prevent abuse)
    max_length = 1000
    if len(review_text) > max_length:
        review_text = review_text[:max_length]
        logger.warning(f"Text truncated to {max_length} characters")
    
    # Empty text handling
    if not review_text or not review_text.strip():
        # Empty text is considered human (no AI detection needed)
        return "HUMAN-WRITTEN", 0.0
    
    # Use EXACT cleaning logic
    review_text = clean_text(review_text)
    
    # Transform and predict
    vector = _vectorizer.transform([review_text])
    probability_ai = _model.predict_proba(vector)[0][1]
    
    # Use EXACT threshold (0.7) - DO NOT MODIFY
    if probability_ai > 0.7:
        label = "AI-GENERATED"
    else:
        label = "HUMAN-WRITTEN"
    
    return label, probability_ai


def is_model_loaded():
    """Check if the model is loaded and ready to use."""
    return _model_loaded and _vectorizer is not None and _model is not None

