# hackathon_14-16.11.2025

ТЗ: https://drive.google.com/drive/folders/1LFTxVDUg-0xxDlET4ickldVZQQrTvZyA

!!! Делать в отдельной ветке, сливать через PR

## Структура проекта
```
project/
 ├── backend/
 │   ├── app.py
 │   ├── models.py
 │   ├── config.py
 │   ├── database.db
 │   ├── requirements.txt
 │   ├── routes/
 │   │   ├── auth.py
 │   │   ├── organizations.py
 │   │   ├── admin.py
 │   │   └── __init__.py
 │   └── utils/
 │       ├── validators.py
 │       ├── security.py
 │       └── __init__.py
 │
 ├── frontend/
 │   ├── index.html
 │   ├── admin.html
 │   ├── login.html
 │   ├── register.html
 │   ├── styles.css
 │   ├── app.js
 │   ├── map.js
 │   └── assets/
 │       ├── logo.png
 │       └── icons/
 ├── README.md
```


# Project: Backend + Frontend (WSL + Windows)

## 0. Start project and cleaning (подробнее каждые действия расписаны ниже)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed
python -m backend.app
# доступ по http://127.0.0.1:5000

rm -rf .venv
rm -f backend/app.db
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```
## Задачи

### 1. Фронтенд UI/UX

**Файлы:**
- `frontend/index.html`
- `frontend/login.html`
- `frontend/register.html`
- `frontend/styles.css`
- `frontend/app.js`
- `frontend/assets/*`

**Функциональность:**
- Главный интерфейс сайта
- Верстка шапки, меню, поиска, списка НКО
- Форма добавления НКО
- Модальные окна: логин, регистрация, карточка НКО
- Адаптивность для мобильных устройств
- JS для связи с бэкендом (fetch API)
- Обработка вывода данных: список НКО, детали НКО
- Базовые подсказки для пользователя

### 2. Интеграция Яндекс.Карт

**Файлы:**
- `frontend/map.js`
- `frontend/index.html` (подключение карты)
- `frontend/assets/icons/markers/*`

**Функциональность:**
- Подключение JS API Яндекс.Карт
- Создание карты с настройкой масштаба и центра
- Добавление меток НКО на карту
- Разные иконки для разных категорий
- Функционал фильтрации меток
- Всплывающие окна по клику на метку
- Управление картой: переход в выбранный город
- Обработка данных, полученных от API

### 3. Бэкенд (API + база данных)

**Файлы:**
- `backend/app.py`
- `backend/models.py`
- `backend/routes/organizations.py`
- `backend/routes/auth.py` (совместно с участником 4)
- `backend/utils/validators.py`
- `backend/database.db`
- `backend/config.py`

**Функциональность:**
- Создание базы данных SQLite
- Реализация моделей SQLAlchemy:
  - `users`
  - `organizations`
  - `pending_organizations`
  - `categories`
  - `cities`
- API для фронтенда:
  - `GET /api/get_organizations`
  - `GET /api/get_cities`
  - `POST /api/add_organization`
  - `POST /api/update_organization`
- Настройка сериализации JSON
- Настройка CORS
- Документирование API
- Тестирование API в Postman

### 4. Авторизация, роли и админка

**Файлы:**
- `frontend/admin.html`
- `frontend/login.html`
- `frontend/register.html`
- `backend/routes/auth.py`
- `backend/routes/admin.py`
- `backend/utils/security.py`

**Функциональность:**
- Система авторизации (Flask-Login):
  - Регистрация
  - Вход
  - Выход
- Ограничение: один пользователь → одна НКО
- Система ролей:
  - Пользователь
  - Администратор
- Админ-панель:
  - Просмотр заявок
  - Одобрение/отклонение
  - Редактирование НКО
- API админки:
  - `GET /api/admin/pending`
  - `POST /api/admin/approve`
  - `POST /api/admin/reject`
  - `GET /api/admin/all`
- Защита маршрутов
- Интеграция админки с фронтендом через fetch