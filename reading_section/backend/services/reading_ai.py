from backend.services.gemini_services import ask_gemini

def get_reading_answer(prompt: str) -> str:
    return ask_gemini(prompt)
