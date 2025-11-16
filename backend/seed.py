# backend/seed.py
import os
from werkzeug.security import generate_password_hash

# Импорты через пакетную структуру
from backend.app import create_app
from backend.models import db, Organization, User

app = create_app()

# Образец данных, на базе вашего sampleNKO, но расширенный полями модели
SAMPLE_ORGS = [
    {
        "name": "Помощь детям",
        "city": "Ангарск",
        "category": "Социальная помощь",
        "description": "Помогаем семьям с детьми",
        "phone": "+7 3842 12-34-56",
        "address": "ул. Ленина, 1",
        "website": "",
        "social_links": "",
        "lat": 52.5369,
        "lon": 103.9368,
        "approved": True
    },
    {
        "name": "Чистый берег",
        "city": "Балаково",
        "category": "Экология",
        "description": "Сбор и переработка мусора",
        "phone": "+7 8453 98-76-54",
        "address": "Набережная, 5",
        "website": "",
        "social_links": "",
        "lat": 51.5381,
        "lon": 46.0245,
        "approved": True
    },
    {
        "name": "Сердце города",
        "city": "Нововоронеж",
        "category": "Культура",
        "description": "Творческие проекты и мероприятия",
        "phone": "+7 4735 77-00-11",
        "address": "Площадь 1",
        "website": "",
        "social_links": "",
        "lat": 51.2999,
        "lon": 39.2358,
        "approved": True
    },
    {
        "name": "Волонтёры здоровья",
        "city": "Обнинск",
        "category": "Медицина",
        "description": "Помощь пожилым и больным",
        "phone": "+7 48439 2-33-44",
        "address": "",
        "website": "",
        "social_links": "",
        "lat": 55.1252,
        "lon": 36.6117,
        "approved": True
    },
    {
        "name": "Помоги лесу",
        "city": "Зеленогорск",
        "category": "Экология",
        "description": "Восстановление лесов",
        "phone": "+7 391 55-66-77",
        "address": "",
        "website": "",
        "social_links": "",
        "lat": 56.1658,
        "lon": 92.4885,
        "approved": True
    },
    {
        "name": "Клуб рукоделия",
        "city": "Заречный",
        "category": "Культура",
        "description": "Творческие мастер-классы",
        "phone": "",
        "address": "",
        "website": "",
        "social_links": "",
        "lat": 55.0380,
        "lon": 60.4080,
        "approved": True
    },
]

with app.app_context():
    print("Пересоздаём базу данных (drop_all -> create_all).")
    # В локальной dev-среде: пересоздать, чтобы гарантировать соответствие схемы.
    db.drop_all()
    db.create_all()

    # Добавляем организации из SAMPLE_ORGS
    if Organization.query.count() == 0:
        print("Добавляем тестовые организации...")
        for org in SAMPLE_ORGS:
            o = Organization(
                name=org["name"],
                city=org.get("city"),
                category=org.get("category"),
                description=org.get("description"),
                phone=org.get("phone"),
                address=org.get("address"),
                website=org.get("website"),
                social_links=org.get("social_links"),
                lat=org.get("lat"),
                lon=org.get("lon"),
                approved=org.get("approved", False)
            )
            db.session.add(o)
    else:
        print("Таблица Organization не пуста, пропускаем добавление организацией из SAMPLE_ORGS.")

    # Создаём дефолтного админа, если его нет
    admin_email = "admin@example.com"
    if User.query.filter_by(email=admin_email).first() is None:
        print("Создаём админа admin@example.com / password")
        admin = User(email=admin_email, password_hash=generate_password_hash("password"), is_admin=True)
        db.session.add(admin)
    else:
        print("Админ уже существует.")

    db.session.commit()
    print("Seed завершён.")
