from pydantic import BaseModel

class EssayRequest(BaseModel):
    username: str
    text: str
    task_type: str