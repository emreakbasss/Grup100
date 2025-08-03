# insert_sample_data.py

from backend.database import SessionLocal, init_db
from backend.models import ReadingPassage, Question

def insert_sample_reading():
    db = SessionLocal()
    init_db()  # Eğer tablo yoksa oluşturur

    # Önceki varsa temizleyebilirsiniz (opsiyonel)
    # db.query(Question).delete()
    # db.query(ReadingPassage).delete()
    # db.commit()

    passage = ReadingPassage(
        title="History of the Internet",
        content=(
            "The history of the Internet dates back to the 1960s when researchers sought to create "
            "a communication network that could survive nuclear attacks. Over several decades, "
            "it evolved to become the global system we use today."
        ),
        level="intermediate"
    )
    db.add(passage)
    db.commit()
    db.refresh(passage)  # passage.id almak için

    questions = [
        Question(
            passage_id=passage.id,
            question_text="When did the history of the Internet begin?",
            choice_a="1950s",
            choice_b="1960s",
            choice_c="1970s",
            choice_d="1980s",
            correct_choice="B"
        ),
        Question(
            passage_id=passage.id,
            question_text="What was a primary goal of the initial network?",
            choice_a="Provide fast communication",
            choice_b="Survive nuclear attacks",
            choice_c="Save money",
            choice_d="Connect all computers worldwide",
            correct_choice="B"
        ),
        Question(
            passage_id=passage.id,
            question_text="How did the network evolve?",
            choice_a="From a local to global system",
            choice_b="Only used by military",
            choice_c="Only text-based communication",
            choice_d="Failed and replaced",
            correct_choice="A"
        ),
        Question(
            passage_id=passage.id,
            question_text="Which word best describes the network now?",
            choice_a="Obsolete",
            choice_b="Global",
            choice_c="Slow",
            choice_d="Limited",
            correct_choice="B"
        ),
        Question(
            passage_id=passage.id,
            question_text="What is the passage mainly about?",
            choice_a="History of the Internet",
            choice_b="Technologies used in the Internet",
            choice_c="Future of communication",
            choice_d="Nuclear warfare",
            correct_choice="A"
        ),
    ]

    db.add_all(questions)
    db.commit()
    db.close()
    print("Veritabanına örnek okuma ve sorular başarıyla eklendi.")

if __name__ == "__main__":
    insert_sample_reading()
