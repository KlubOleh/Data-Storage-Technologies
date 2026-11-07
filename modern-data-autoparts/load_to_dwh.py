"""
Завантаження (Load) Parquet-файлів з data_lake/ у схему raw PostgreSQL DWH.
Дані завантажуються "як є" (as is) — без очищення.

Ідемпотентність: перед кожним завантаженням таблиця видається з CASCADE.
Це потрібно, бо після `dbt run` від таблиць raw залежать staging-views, і звичайний
DROP TABLE (який виконує if_exists='replace') падав би з помилкою DependentObjectsStillExist.
CASCADE прибирає ці views, а наступний `dbt run` у конвеєрі створює їх заново.

Таблиці визначаються автоматично за файлами data_lake/raw_*.parquet.
"""
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminpassword")
DB_NAME = os.getenv("DB_NAME", "autoparts_dwh")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATA_DIR = "data_lake"


def load_data_to_dwh():
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

    files = sorted(Path(DATA_DIR).glob("raw_*.parquet"))
    if not files:
        raise FileNotFoundError(f"У папці {DATA_DIR}/ немає файлів raw_*.parquet. Спершу запустіть data_generator.py")

    for file in files:
        table = file.stem.removeprefix("raw_")
        df = pd.read_parquet(file)
        print(f"Завантаження {table} ({len(df)} рядків)...")
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS raw."{table}" CASCADE'))
        df.to_sql(table, engine, schema="raw", if_exists="replace", index=False)

    print("Дані успішно завантажені у схему 'raw'!")


if __name__ == "__main__":
    load_data_to_dwh()
