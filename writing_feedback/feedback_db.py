import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import pytz

Base = declarative_base()
turkey_tz = pytz.timezone("Europe/Istanbul")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    essay_text = Column(String)
    task_type = Column(String)
    band_task = Column(Float)
    band_coherence = Column(Float)
    band_lexical = Column(Float)
    band_grammar = Column(Float)
    band_overall = Column(Float)
    evaluation_text = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(tz=turkey_tz))

# ✅ Veritabanını hep backend klasörü altına sabitle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "feedbacks.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
