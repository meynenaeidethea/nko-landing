# Скрипт для заполнения БД тестовыми данными.
from backend.app import create_app
from backend.models import db, Organization, User
from werkzeug.security import generate_password_hash
import os

app = create_app()

sample = [
  dict(name="Помощь детям", city="Ангарск", category="Социальная помощь", description="Помогаем семьям с детьми", phone="+7 3842 12-34-56", address="ул. Ленина, 1", website="", social_links="", lat=52.5369, lon=103.9368, approved=True),
  dict(name="Чистый берег", city="Балаково", category="Экология", description="Сбор и переработка мусора", phone="+7 8453 98-76-54", address="Набережная, 5", website="", social_links="", lat=51.5381, lon=46.0245, approved=True),
  dict(name="Сердце города", city="Нововоронеж", category="Культура", description="Творческие проекты и мероприятия", phone="+7 4735 77-00-11", address="Площадь 1", website="", social_links="", lat=51.2999, lon=39.2358, approved=True),
]

with app.app_context():
    db.create_all()
    # add sample orgs if none exist
    if Organization.query.count() == 0:
        for s in sample:
            org = Organization(**s)
            db.session.add(org)
        # add sample admin user
        if User.query.filter_by(email='admin@example.com').first() is None:
            u = User(email='admin@example.com', password=generate_password_hash('password'), is_admin=True)
            db.session.add(u)
        db.session.commit()
        print('Seed data inserted.')
    else:
        print('DB already has data.')
