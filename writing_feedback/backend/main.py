from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.model import evaluate_essay, correct_essay, improve_essay, analyze_essay
from feedback_db import Feedback, SessionLocal
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EssayRequest(BaseModel):
    username: str
    text: str
    task_type: str


@app.post("/evaluate")
@app.post("/evaluate")
async def evaluate(request: EssayRequest):
    print(f"📥 Evaluate called with user {request.username}")
    try:
        result = await evaluate_essay(request.text, request.task_type)
        print("✅ Evaluation result received")
    except Exception as e:
        print("❌ Error during evaluation:", e)
        raise HTTPException(status_code=500, detail="Evaluation failed")

    try:
        def extract_band(title):
            import re
            match = re.search(rf"{title} \(Band ([0-9.]+)\)", result["evaluation"])
            return float(match.group(1)) if match else None

        feedback = Feedback(
            username=request.username,
            essay_text=request.text,
            task_type=request.task_type,
            band_task=extract_band("Task"),
            band_coherence=extract_band("Coherence and Cohesion"),
            band_lexical=extract_band("Lexical Resource"),
            band_grammar=extract_band("Grammatical Range and Accuracy"),
            band_overall=extract_band("Overall Band Score"),
            evaluation_text=result["evaluation"]
        )

        db = SessionLocal()
        db.add(feedback)
        db.commit()
        print("✅ Feedback saved to DB for:", request.username)
    except Exception as e:
        print("❌ DB kayıt hatası:", e)
        raise HTTPException(status_code=500, detail="DB error")
    finally:
        db.close()

    return result

@app.get("/history/{username}")
def get_history(username: str):
    db = SessionLocal()
    records = db.query(Feedback).filter(Feedback.username == username).order_by(Feedback.created_at).all()
    db.close()

    return [
        {
            "date": record.created_at.strftime("%Y-%m-%d %H:%M"),
            "overall": record.band_overall,
            "task": record.band_task,
            "coherence": record.band_coherence,
            "lexical": record.band_lexical,
            "grammar": record.band_grammar,
            "evaluation": record.evaluation_text
        } for record in records
    ]

@app.post("/correct")
async def correct(request: EssayRequest):
    result = await correct_essay(request.text)
    return {
        "highlighted_text": result["highlighted_text"],
        "corrected_text": result["corrected_text"]
    }

@app.post("/improve")
async def improve(request: EssayRequest):
    improved_text = await improve_essay(request.text)
    return {"improved_text": improved_text}

@app.post("/analyze")
async def analyze_endpoint(request: EssayRequest):
    return await analyze_essay(request.text)