from backend.services.gemini_service import ask_gemini

def generate_response(prompt: str) -> str:
    return ask_gemini(prompt)
