import google.generativeai as genai
import os

# Replace with your API key OR use environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyCSOPD3NdLmkdE12JJ7FatZJ2scWVi6EXM")

MODEL_NAME = "gemini-1.5-pro"  # change if needed

try:
    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(
        "Reply with exactly this text: Gemini API is working."
    )

    print("✅ Gemini Response:")
    print(response.text)

except Exception as e:
    print("❌ Gemini API Error:")
    print(type(e).__name__, str(e))
