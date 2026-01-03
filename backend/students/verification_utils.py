"""
OCR and verification utilities - EXACT SAME CODE AS ID_verifying/app.py
"""
import pytesseract
import cv2
import re
from rapidfuzz import fuzz
import base64
import numpy as np

# Set Tesseract path for Windows - same as Flask version
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def normalize(text):
    """EXACT SAME as Flask version"""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def fuzzy(a, b):
    """EXACT SAME as Flask version"""
    return fuzz.partial_ratio(normalize(a), normalize(b))


def extract_text(image_file):
    """
    EXACT SAME as Flask version - extract_text(image_path)
    """
    # Read image data
    image_data = image_file.read()
    image_file.seek(0)
    
    # Convert to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    
    # Decode image - same as cv2.imread in Flask
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # EXACT SAME preprocessing as Flask
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    
    # EXACT SAME OCR
    text = pytesseract.image_to_string(gray)
    return text.lower()


def verify_student_id(image_file, college_name, student_name, usn, email=None):
    """
    EXACT SAME logic as Flask version - index() route
    """
    # Read image data for storage
    image_file.seek(0)
    image_data = image_file.read()
    image_file.seek(0)
    
    # EXACT SAME as Flask: ocr_text = extract_text(image_path)
    ocr_text = extract_text(image_file)
    
    # EXACT SAME as Flask: college_score = fuzzy(college, ocr_text)
    college_score = fuzzy(college_name, ocr_text)
    name_score = fuzzy(student_name, ocr_text)
    usn_score = fuzzy(usn, ocr_text)
    
    # EXACT SAME as Flask: email_domain logic
    domain_score = 0
    if email and "@" in email:
        email_domain = email.split("@")[-1]
        domain_score = fuzzy(email_domain, ocr_text)
    
    # EXACT SAME verification logic as Flask
    verified = (
        college_score >= 75 and
        name_score >= 75 and
        (usn_score >= 90 or domain_score >= 80)
    )
    
    # Encode image to base64 for response
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # EXACT SAME result format as Flask
    result = {
        "verified": verified,
        "college_score": college_score,
        "name_score": name_score,
        "usn_score": usn_score,
        "image_base64": image_base64
    }
    
    if email:
        result["domain_score"] = domain_score
    
    return result

