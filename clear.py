from database import SessionLocal
from models import GameSession

def clear_sessions():
    db = SessionLocal()
    try:
        count = db.query(GameSession).count()
        db.query(GameSession).delete()
        db.commit()
        print(f"Удалено {count} сессий")
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("Вы уверены? Все данные будут удалены! (да/нет): ")
    if confirm.lower() == "да":
        clear_sessions()
    else:
        print("Отменено")