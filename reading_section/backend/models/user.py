from typing import Optional
from pydantic import BaseModel , EmailStr

class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: bool = False

    class Config:
        orm_mode = True # SQLAlchemy kolay kullanım


