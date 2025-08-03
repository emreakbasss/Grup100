from sqlalchemy import (Column, Integer, String,
ForeignKey, Text)
from sqlalchemy.orm import relationship
from backend.models.base import Base

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer,
ForeignKey('reading_passages.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    choice_a = Column(String(255), nullable=False)
    choice_b = Column(String(255), nullable=False)
    choice_c = Column(String(255), nullable=False)
    choice_d = Column(String(255), nullable=False)
    correct_choice = Column(String(1), nullable=False)  # 'A', 'B', 'C' veya 'D'

    # İlişkiyi ReadingPassage ile kuruyoruz
    passage = relationship("ReadingPassage",
back_populates="questions")
