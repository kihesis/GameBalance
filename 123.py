from database import SessionLocal
from models import GameSession

db = SessionLocal()
try:
    test_record = GameSession(hours=1.5, mood="Тест")
    db.add(test_record)
    db.commit()
    print("✅ Запись добавлена вручную!")
except Exception as e:
    print("❌ Ошибка:", e)
    db.rollback()
finally:
    db.close()