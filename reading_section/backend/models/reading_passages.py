from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.models.base import Base

class ReadingPassage(Base):
    __tablename__ = "reading_passages"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    level = Column(String(50), nullable=True)

    questions = relationship("Question", back_populates="passage", cascade="all, delete")
