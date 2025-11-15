import pandas as pd
from app import app
from models import db, Organization

EXCEL_FILE = "table.xlsm"

with app.app_context():

    print(f"Читаем файл: {EXCEL_FILE}")
    xls = pd.ExcelFile(EXCEL_FILE)
    print("Найдены листы:", xls.sheet_names)

    total_added = 0

    for sheet_name in xls.sheet_names:

        print(f"\n=== Обрабатываем лист: {sheet_name} ===")
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=1)

        df = df.rename(columns={
            "Деятельность НКО": "category",
            "Название организации": "name",
            "Про организацию": "description",
            "Ссылка на социальные сети": "social_links"
        })

        print("Колонки после чтения:", df.columns.tolist())

        added = 0

        for _, row in df.iterrows():

            if not isinstance(row.get("name"), str) or not row["name"].strip():
                continue

            org = Organization(
                name=row["name"].strip(),
                city=sheet_name, 
                category=row.get("category", ""),
                description=row.get("description", ""),
                social_links=row.get("social_links", "")
            )

            db.session.add(org)
            added += 1

        db.session.commit()
        total_added += added

        print(f"Добавлено организаций на листе '{sheet_name}': {added}")

    print("\n=== Импорт завершён ===")
    print(f"Всего добавлено организаций: {total_added}")
