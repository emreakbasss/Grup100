# backend/api/default_routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "API çalışıyor!"}

@router.post("/ask")
def ask_question():
    # Örnek placeholder endpoint
    return {"answer": "Bu endpoint henüz implement edilmedi."}

