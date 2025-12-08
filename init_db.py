from database import engine, Base
from models import GameSession

print("Создаём таблицы...")
Base.metadata.create_all(bind=engine)
print("✅ Готово!")