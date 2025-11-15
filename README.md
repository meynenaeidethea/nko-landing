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

## 1. Installation

### 1.1 Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 1.2 Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Initialize database
If old schema exists, remove it:
```bash
rm -f backend/app.db
```

Then populate seed data:
```bash
python -m backend.seed
```

## 3. Run backend
Always run Flask like this:
```bash
python -m backend.app
```

## 4. Run frontend
```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory frontend
```

## 5. Stop services
Press **Ctrl + C** in each terminal window.

## 6. Clean project
```bash
rm -rf .venv
rm -f backend/app.db
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```