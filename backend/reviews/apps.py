from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    
    def ready(self):
        """Load ML model when Django app is ready."""
        try:
            from .review_checker import load_model
            success = load_model()
            if success:
                logger.info("ML model loaded successfully at startup")
            else:
                logger.warning("ML model failed to load. AI detection will not work until model files are available.")
        except Exception as e:
            logger.error(f"Error loading ML model at startup: {str(e)}", exc_info=True)

