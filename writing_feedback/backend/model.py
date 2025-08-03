import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-pro')


async def generate_content_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    # Simulating async generation process
    return await loop.run_in_executor(None, lambda: model.generate_content(prompt).text)


async def evaluate_essay(text: str, task_type: str) -> dict:
    prompt = f"""
    You are a certified IELTS examiner.
    Evaluate the following {task_type} writing response using the four IELTS criteria:
    -Task Achievement or Task Response
    -Coherence and Cohesion
    -Lexical Resource
    -Grammatical Range and Accuracy

    For each category:
    - Assign a band score (0 to 9)
    - Give Overall Band Score as **Overall Band Score (Band ...)**
    - Give a short explanation    Student response:

    {text}
    """
    try:
        evaluation_text = await generate_content_async(prompt)  # Asenkron içerik oluşturma
        return {"evaluation": evaluation_text}
    except Exception as e:
        print(f"Error in evaluate_essay: {e}")
        return {"error": "Error generating evaluation from the model."}


async def correct_essay(text: str) -> dict:
    prompt = f"""
    You are an English writing assistant. Respond only in JSON. The student has written the following text. Your task is to:

    1. Identify and highlight all grammatical, spelling, punctuation, and structural mistakes.
    2. For each mistake, wrap the incorrect part in <span class='error' data-tooltip='EXPLANATION'>WRONG</span>
    3. Then, generate a corrected version of the entire text (without highlights).

    Return exactly:
    {{
      "highlighted_text": "Use <span class='error'>wrong</span> format here",
      "corrected_text": "Correct sentence here"
    }}

    Respond ONLY with valid JSON. Do NOT include markdown (like ```json). If you include quotes inside strings (e.g. in data-tooltip), escape them using \". Your response must be directly parsable by json.loads().
    Student's original text:
    {text}
    """
    response_text = await generate_content_async(prompt)
    raw = response_text.strip()

    # remove ```json or ``` at start/end if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        return {
            "highlighted_text": f"<pre>{text}</pre>",
            "corrected_text": text
        }


async def improve_essay(text: str) -> str:
    prompt = f"""
    You are an academic writing coach. Improve the following IELTS writing response to sound more fluent, cohesive, and sophisticated.
    - Use better vocabulary and sentence structures.
    - Make it sound like a high Band 9 IELTS essay.
    - Keep the original ideas, but enhance the expression.
    - Return only the improved version. Do not explain.

    Original text:
    {text}
    """
    response_text = await generate_content_async(prompt)
    return response_text


async def analyze_essay(text: str) -> dict:
    prompt = f"""
    Analyze the following student essay in English. Respond ONLY in pure JSON, and do NOT use markdown like ```json. Return a JSON with the following keys:

    {{
      "word_count": number of words in the text,
      "grammar_mistake_count": total number of grammar, punctuation, or structural mistakes,
      "vocab_repetition": [{{"word": "repeatedWord", "count": 5}}, ... top 5 repeated non-stop words],
      "vocab_levels": {{
          "A1": 5,
          "A2": 10,
          "B1": 15,
          "B2": 8,
          "C1": 2,
          "C2": 0
      }}
    }}

    Do not explain anything. Only output valid JSON that can be parsed directly by json.loads().
    Student's text:
    {text}
    """

    response_text = await generate_content_async(prompt)
    raw = response_text.strip()

    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print("JSON decode error in analyze_essay:", e)
        return {
            "word_count": 0,
            "grammar_mistake_count": 0,
            "vocab_repetition": [],
            "vocab_levels": {
                "A1": 0, "A2": 0, "B1": 0, "B2": 0, "C1": 0, "C2": 0
            }
        }