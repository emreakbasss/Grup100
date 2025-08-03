# listening_generator.py
import google.generativeai as genai
from config import GEMINI_API_KEY
import json

# Gemini API yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_listening_example():
    prompt = """
    You are an IELTS content creator. Generate a 3-turn dialogue in the IELTS Listening Part 1 style.

    Format strictly as:
    A: [...]
    B: [...]
    A: [...]

    Then, based on that conversation, generate one multiple-choice question (MCQ) with 4 options (A–D).
    Indicate the correct answer clearly.

    Return the result as a JSON object:
    {
        "dialogue": ["A: ...", "B: ...", "A: ..."],
        "question": "...",
        "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
        "answer": "..."
    }
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    result = generate_listening_example()
    print("--- Listening Example ---")
    print(result)

    # Test için JSON parse
    try:
        parsed = json.loads(result)
        print("\nParsed JSON:")
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print("Parsing error:", e)
