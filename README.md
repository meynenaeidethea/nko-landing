# Карта добрых дел

Интерактивная карта НКО и волонтёрских инициатив: пользователи ищут организации по городу и категории на карте, могут предложить новую НКО, а администраторы модерируют заявки.

Изначально проект делался на хакатоне, сейчас доведён до презентабельного состояния как публичный pet-проект.

## Стек

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-CORS, JWT-авторизация (PyJWT), SQLite
- **Frontend:** статические HTML-страницы, Bootstrap 5, Яндекс.Карты (JS API), vanilla JS

## Структура проекта

```
.
├── backend/
│   ├── app.py            # фабрика приложения, регистрация роутов
│   ├── models.py          # модели SQLAlchemy (User, Organization, ...)
│   ├── config.py           # конфигурация Flask/JWT
│   ├── seed.py             # наполнение БД тестовыми данными
│   ├── routes/
│   │   ├── auth.py          # /api/auth — регистрация, вход, /me
│   │   ├── organizations.py # /api/organizations — список, создание, "мои"
│   │   └── admin.py         # /api/admin — модерация заявок
│   └── utils/
│       ├── validators.py
│       ├── security.py
│       └── jwt_utils.py
├── frontend/
│   ├── index.html          # главная карта
│   ├── login.html / register.html
│   ├── admin.html          # админ-панель модерации
│   ├── add_organization.html
│   ├── style.css / map.css
│   ├── map.js               # интеграция Яндекс.Карт
│   └── assets/
└── requirements.txt
```

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed     # создаёт БД и наполняет тестовыми НКО + админом
python -m backend.app
# бэкенд поднимется на http://127.0.0.1:5000
```

Фронтенд — статические файлы в `frontend/`, backend отдаёт их через `send_from_directory` (см. `backend/app.py`), поэтому после `python -m backend.app` сайт доступен по тому же адресу.

Для работы карты нужен свой ключ Яндекс.Карт JS API: подставьте его вместо `ваш API-ключ` в `frontend/index.html` (строка с `api-maps.yandex.ru`).

После `python -m backend.seed` доступен тестовый администратор:

```
email:    admin@example.com
password: password
```

Это dev-заглушка для локальной проверки админки — не использовать в проде.

## Очистка окружения

```bash
rm -rf .venv
rm -f backend/database.db
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Основные API-эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/auth/register` | регистрация пользователя |
| POST | `/api/auth/login` | вход, выдаёт JWT |
| GET  | `/api/auth/me` | текущий пользователь |
| GET  | `/api/organizations/` | список одобренных НКО |
| POST | `/api/organizations/` | предложить новую НКО (на модерацию) |
| GET  | `/api/organizations/my` | НКО текущего пользователя |
| GET  | `/api/admin/pending` | заявки на модерации (только админ) |
| POST | `/api/admin/approve/<id>` | одобрить заявку |
| POST | `/api/admin/reject/<id>` | отклонить заявку |
