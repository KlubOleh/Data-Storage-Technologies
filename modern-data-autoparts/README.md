# Modern Data Stack: Магазин автозапчастин (Варіант 5)

Навчальний проєкт з дисципліни «Технології сховищ даних» (НУ «Львівська політехніка», кафедра ЕОМ).
Повноцінний ELT-конвеєр: **Python → PostgreSQL (Docker) → dbt → Airflow → Metabase**.

> Етапи: **ЛР №1 — Data Ingestion (Extract & Load)** ✅, **ЛР №2 — Transform (dbt, Star Schema)** ✅.

## Предметна область
Магазин автозапчастин.

| Таблиця | Тип | Опис |
|---|---|---|
| `manufacturers` | Dimension | Виробники запчастин |
| `parts` | Dimension | Запчастини (FK → manufacturers) |
| `car_owners` | Dimension | Власники авто (клієнти) |
| `sales` | **Fact** | Продажі (FK → car_owners, parts) |
| `returns` | **Fact** | Повернення (FK → sales, car_owners, parts) |

Навмисні «брудні» дані (для очищення в dbt у ЛР №2): ~10% `NULL` у `car_owners.email`,
~5% дублікатів `car_owners`, ~20% `NULL` у `returns.comment`.

## Архітектура
```
Faker (Python, контейнер) → Parquet (data_lake/) → PostgreSQL (Docker), схема raw
```

## Вимоги
Лише **Docker Desktop** (Python локально не потрібен).

## Запуск
```bash
# 1. Запустити сховище
docker compose up -d

# 2. Згенерувати дані та завантажити в схему raw
docker compose run --rm data_loader
```
Повторний запуск безпечний (ідемпотентність: `if_exists='replace'`).

## Перевірка результату
```bash
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "\dt raw.*"
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "SELECT COUNT(*) FROM raw.sales;"
```
Підключення з DBeaver/pgAdmin: `localhost:5432`, БД `autoparts_dwh`, користувач `admin`, пароль `adminpassword`.

## ЛР №2: dbt і схема «Зірка»
dbt запускається в Docker (`Dockerfile.dbt`), локальне встановлення не потрібне.
```bash
docker compose up -d
docker compose run --rm dbt debug   # перевірка підключення
docker compose run --rm dbt run     # побудова моделей у схемі analytics
```

### Структура dbt-проєкту (`autoparts_dbt/`)
```
models/
├── staging/                 # views: очищення, перейменування, типи
│   ├── src_autoparts.yml    # опис джерел (schema raw)
│   ├── stg_manufacturers.sql
│   ├── stg_parts.sql        # фільтр price >= 0
│   ├── stg_car_owners.sql   # дедуплікація (row_number), coalesce(email)
│   ├── stg_sales.sql
│   └── stg_returns.sql      # coalesce(comment)
└── marts/                   # tables: схема «Зірка»
    ├── dim_manufacturers.sql
    ├── dim_parts.sql        # + дані виробника
    ├── dim_car_owners.sql
    ├── fct_sales.sql        # total_amount = quantity * unit_price
    └── fct_returns.sql
```

### Схема «Зірка»
```
dim_car_owners ─┐
dim_parts ──────┼── fct_sales        dim_car_owners ─┐
dim_manufact. ──┘                    dim_parts ──────┼── fct_returns
```

## Структура репозиторію
```
.
├── docker-compose.yml   # PostgreSQL + одноразовий контейнер data_loader
├── Dockerfile           # образ Python для скриптів
├── Dockerfile.dbt       # образ dbt (dbt-core 1.8.8 + dbt-postgres 1.8.2)
├── autoparts_dbt/       # dbt-проєкт (ЛР №2)
├── data_generator.py    # генерація даних (Faker) → data_lake/*.parquet
├── load_to_dwh.py       # завантаження Parquet → схема raw
├── requirements.txt
└── README.md
```

## Зупинка
```bash
docker compose down        # зупинити
docker compose down -v     # зупинити і видалити дані БД
```
