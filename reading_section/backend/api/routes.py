from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth.auth import get_current_user
from backend.services.logic import generate_response

router = APIRouter(prefix="/api", tags=["ai"])

class PromptRequest(BaseModel):
    prompt: str

@router.post("/ask")
def ask_ai(
    req: PromptRequest,
    user: str = Depends(get_current_user)
):
    answer = generate_response(req.prompt)
    return {"response": answer}
