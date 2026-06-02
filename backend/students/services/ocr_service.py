import re
import base64
import difflib
from typing import List, Tuple, Optional, Dict, Any

import cv2
import numpy as np
import easyocr

USN_PATTERN = re.compile(r"\b[1-9][A-Z]{2,3}\d{2}[A-Z]{2}\d{3}\b", re.IGNORECASE)
COLLEGE_KEYWORDS = re.compile(
    r"\b(college|institute|university|engineering|academy|school|technology|science)\b",
    re.IGNORECASE,
)
NAME_LABELS = re.compile(r"\b(student\s*name|name|candidate|identity)\b", re.IGNORECASE)

OCR_READER = easyocr.Reader(["en"], gpu=False)


def _normalize_text(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def _read_image_bytes(image_file) -> Tuple[bytes, np.ndarray]:
    image_file.seek(0)
    data = image_file.read()
    if not data:
        raise ValueError("Uploaded image is empty or unreadable")

    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unsupported image format or corrupted image")

    return data, image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    height, width = gray.shape[:2]
    if width > 1400 or height > 1400:
        scale = min(1400 / width, 1400 / height)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    elif width < 600 or height < 600:
        scale = max(600 / width, 600 / height)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    kernel = np.ones((2, 2), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    return gray


def extract_text_easyocr(image: np.ndarray) -> Tuple[str, float, List[Tuple[Any, str, float]]]:
    results = OCR_READER.readtext(image, detail=1, paragraph=False)
    if not results:
        return "", 0.0, []

    words = [text for _, text, _ in results]
    raw_text = " ".join(words).strip()
    confidence_list = [float(confidence) for _, _, confidence in results if confidence is not None]
    confidence = float(np.mean(confidence_list)) if confidence_list else 0.0

    return raw_text, confidence, results


def extract_usn(raw_text: str) -> List[str]:
    if not raw_text:
        return []

    normalized = raw_text.replace(" ", "").replace("-", "").replace("_", "")
    matches = USN_PATTERN.findall(raw_text) or USN_PATTERN.findall(normalized)
    return [match.upper() for match in matches]


def _detect_name(raw_text: str) -> str:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        if NAME_LABELS.search(line):
            cleaned = re.split(r"name\s*[:\-]\s*", line, flags=re.IGNORECASE)
            if len(cleaned) > 1 and cleaned[1].strip():
                return cleaned[1].strip()

    candidates = [line for line in lines if re.match(r"^[A-Za-z ]{6,}$", line) and not re.search(r"\d", line)]
    if candidates:
        return max(candidates, key=len)

    return ""


def _detect_college(raw_text: str) -> str:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        if COLLEGE_KEYWORDS.search(line) and not USN_PATTERN.search(line):
            return line.strip()

    candidate_lines = [line for line in lines if len(line) > 15 and re.search(r"\b[A-Za-z ]+\b", line)]
    if candidate_lines:
        return max(candidate_lines, key=len)

    return ""


def _choose_usn(candidates: List[str], expected_usn: str) -> str:
    if not candidates:
        return ""

    normalized_expected = _normalize_text(expected_usn)
    for candidate in candidates:
        if _normalize_text(candidate) == normalized_expected:
            return candidate

    return candidates[0]


def _similarity(a: str, b: str) -> float:
    a_norm = re.sub(r"[^A-Za-z0-9]", "", a.lower())
    b_norm = re.sub(r"[^A-Za-z0-9]", "", b.lower())
    if not a_norm or not b_norm:
        return 0.0
    return difflib.SequenceMatcher(None, a_norm, b_norm).ratio()


def verify_student_id(image_file, college_name: str, student_name: str, usn: str, email: Optional[str] = None) -> Dict[str, Any]:
    image_data, image = _read_image_bytes(image_file)
    preprocessed = preprocess_image(image)
    raw_text, confidence, _ocr_results = extract_text_easyocr(preprocessed)

    detected_usns = extract_usn(raw_text)
    detected_usn = _choose_usn(detected_usns, usn)
    detected_student_name = _detect_name(raw_text)
    detected_college_name = _detect_college(raw_text)

    college_score = int(round(100 * _similarity(college_name, raw_text)))
    name_score = int(round(100 * _similarity(student_name, raw_text)))
    usn_score = int(round(100 * _similarity(usn, raw_text)))

    domain_score = 0
    if email and "@" in email:
        email_domain = email.split("@")[-1]
        domain_score = int(round(100 * _similarity(email_domain, raw_text)))

    verified = college_score >= 75 and name_score >= 75 and (usn_score >= 90 or domain_score >= 80)

    image_base64 = base64.b64encode(image_data).decode("utf-8")

    result = {
        "verified": verified,
        "success": verified,
        "usn_detected": detected_usn,
        "student_name_detected": detected_student_name,
        "college_name_detected": detected_college_name,
        "raw_text": raw_text,
        "confidence": round(float(confidence), 2),
        "college_score": college_score,
        "name_score": name_score,
        "usn_score": usn_score,
        "image_base64": image_base64,
    }
    if email:
        result["domain_score"] = domain_score

    return result
