from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import SessionLocal
from backend.models import ReadingPassage, Question
from backend.auth.auth import get_current_user

router = APIRouter()


class ReadingRequest(BaseModel):
    level: str = "intermediate"


@router.post("/reading_section")
def get_reading_section(data: ReadingRequest, current_user: str = Depends(get_current_user)):
    # Sabit örnek veri, istersen veritabanından alabilirsin
    if data.level != "intermediate":
        raise HTTPException(404, "Okuma metni bulunamadı")


    passage = db.query(ReadingPassage).filter_by(level=data.level).first()
    if not passage:
        raise HTTPException(404, "Okuma metni bulunamadı.")
    questions = db.query(Question).filter_by(passage_id=passage.id).all()
    return {
        "reading_passage": {
            "id": passage.id,
            "title": passage.title,
            "content": passage.content,
            "level": passage.level,
        },
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "choices": {"A": q.choice_a, "B": q.choice_b, "C": q.choice_c, "D": q.choice_d},
            }
            for q in questions
        ],
    }
