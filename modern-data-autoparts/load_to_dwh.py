"""
Завантаження (Load) Parquet-файлів з data_lake/ у схему raw PostgreSQL DWH.
Дані завантажуються "як є" (as is) — без очищення.
if_exists='replace' робить скрипт ідемпотентним (безпечний перезапуск).
"""
import os

import pandas as pd
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminpassword")
DB_NAME = os.getenv("DB_NAME", "autoparts_dwh")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATA_DIR = "data_lake"
TABLES = ["manufacturers", "parts", "car_owners", "sales", "returns", "reviews"]

def load_data_to_dwh():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()
    for table in TABLES:
        df = pd.read_parquet(f"{DATA_DIR}/raw_{table}.parquet")
        print(f"Завантаження {table} ({len(df)} рядків)...")
        df.to_sql(table, engine, schema="raw", if_exists="replace", index=False)
    print("Дані успішно завантажені у схему 'raw'!")
if __name__ == "__main__":
    load_data_to_dwh()
