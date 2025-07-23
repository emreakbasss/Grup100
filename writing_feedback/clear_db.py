from feedback_db import SessionLocal, Feedback

db = SessionLocal()
db.query(Feedback).delete()
db.commit()
db.close()

print("Tüm kayıtlar silindi.")
