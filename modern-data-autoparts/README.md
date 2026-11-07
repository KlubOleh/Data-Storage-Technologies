# Modern Data Stack: Магазин автозапчастин (Варіант 5)

Навчальний проєкт з дисципліни «Технології сховищ даних» (НУ «Львівська політехніка», кафедра ЕОМ).
Повноцінний ELT-конвеєр: **Python → PostgreSQL (Docker) → dbt → Airflow → Metabase**.

> Етапи: **ЛР №1 — Data Ingestion (Extract & Load)** ✅, **ЛР №2 — Transform (dbt, Star Schema)** ✅, **ЛР №3 — Orchestration (Airflow, Data Quality Gates)** ✅.

## Предметна область
Магазин автозапчастин.

| Таблиця | Тип | Опис |
|---|---|---|
| `manufacturers` | Dimension | Виробники запчастин |
| `parts` | Dimension | Запчастини (FK → manufacturers) |
| `car_owners` | Dimension | Власники авто (клієнти) |
| `sales` | **Fact** | Продажі (FK → car_owners, parts) |
| `returns` | **Fact** | Повернення (FK → sales, car_owners, parts) |
| `reviews` | **Fact** | Відгуки на запчастини (завдання 2 методички: `product_id` → parts, `user_id` → car_owners, `rating` 1–5, `comment`) |

> Таблиця `reviews` завантажується в схему `raw` (ЛР №1). У dbt-моделях ЛР №2 вона не використовується.

Навмисні «брудні» дані (для очищення в dbt у ЛР №2): ~10% `NULL` у `car_owners.email`,
~5% дублікатів `car_owners`, ~20% `NULL` у `returns.comment` та `reviews.comment`.

## Архітектура
```
Faker (Python) → Parquet (data_lake/) → PostgreSQL, схема raw → dbt (staging → marts) → dbt test
└──────────────────────── усе керується Apache Airflow (DAG autoparts_elt_pipeline) ────────────┘
```

## Вимоги
Лише **Docker Desktop** (Python локально не потрібен).

## Запуск
```bash
# 1. Запустити лише сховище (PostgreSQL)
docker compose up -d dwh_postgres

# 2. Згенерувати дані та завантажити в схему raw
docker compose run --rm data_loader
```
Повторний запуск безпечний (ідемпотентність): перед завантаженням кожна таблиця видаляється з `CASCADE`.
Це потрібно, бо після `dbt run` від таблиць `raw` залежать staging-views, і звичайний `DROP TABLE`
(який виконує `if_exists='replace'`) завершувався б помилкою `DependentObjectsStillExist`.
Views одразу відновлюються наступним `dbt run`.

## Перевірка результату
```bash
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "\dt raw.*"
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "SELECT COUNT(*) FROM raw.sales;"
```
Підключення з DBeaver/pgAdmin: `localhost:5432`, БД `autoparts_dwh`, користувач `admin`, пароль `adminpassword`.

## Версії за лабораторними
Стан репозиторію після ЛР №1 зафіксовано релізом [`Lab_1`](https://github.com/KlubOleh/Data-Storage-Technologies/releases/tag/Lab_1). Актуальна версія — у гілці `main`.

## ЛР №2: dbt і схема «Зірка»
dbt запускається в Docker (`Dockerfile.dbt`), локальне встановлення не потрібне.
```bash
docker compose up -d
docker compose run --rm dbt debug   # перевірка підключення
docker compose run --rm dbt run     # побудова моделей у схемі analytics
```

Перевірка результату (5 таблиць marts і 5 views staging у схемі `analytics`):
```bash
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "\dt analytics.*" -c "\dv analytics.*"
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "SELECT (SELECT COUNT(*) FROM raw.car_owners) AS raw_rows, (SELECT COUNT(*) FROM analytics.dim_car_owners) AS dim_rows;"
```
Очищення працює без видалення даних: `raw.car_owners` (630 рядків із дублікатами) лишається незмінною, а `analytics.dim_car_owners` містить 600 унікальних власників.

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

## ЛР №3: оркестрація (Airflow) і Data Quality Gates
Apache Airflow працює в Docker (`Dockerfile.airflow`, образ `apache/airflow:2.10.5`), локальне встановлення не потрібне.

```bash
docker compose up -d --build     # перший запуск: збірка образу Airflow займає кілька хвилин
```
Web UI: <http://localhost:8080> (логін `admin`, пароль `admin`). Airflow стартує 1–2 хвилини.

1. Знайдіть DAG **`autoparts_elt_pipeline`**, увімкніть перемикач зліва від назви.
2. Натисніть кнопку **Trigger DAG** (▶).
3. Відкрийте вкладку **Graph** і дочекайтеся, поки всі три таски стануть зеленими.

```
extract_and_load_raw_data  →  dbt_run_transformations  →  dbt_test_task
   PythonOperator (ЛР №1)       BashOperator (ЛР №2)       BashOperator (Data Quality Gate)
```

![Airflow Graph](images/airflow_graph.png)

### Data Quality Gates
Файл `autoparts_dbt/models/staging/schema.yml` містить 18 тестів: `unique` та `not_null` для ключів
(зокрема `owner_id` у `stg_car_owners`), `relationships` між staging-моделями (цілісність зв'язків)
та `accepted_values` для `payment_method`. Таск `dbt_test_task` виконується **лише після** успішного
`dbt run`; якщо хоча б один тест падає, таск (і весь DAG) стає червоним.

Перевірка «воріт»: зіпсуйте дані й запустіть `dbt test` —
```bash
docker exec -it dwh_postgres psql -U admin -d autoparts_dwh -c "UPDATE raw.sales SET payment_method='crypto' WHERE sale_id=(SELECT sale_id FROM raw.sales LIMIT 1);"
docker compose run --rm dbt test        # FAIL: accepted_values_stg_sales_payment_method
```
(наступний запуск DAG перезавантажить raw і виправить дані).

### Особливості реалізації
* Python-скрипти та dbt працюють у **окремих віртуальних середовищах** усередині контейнера Airflow
  (`/home/airflow/venvs/etl` і `/home/airflow/venvs/dbt`), бо Airflow використовує SQLAlchemy 1.4,
  а pandas 2.x та dbt вимагають інших версій. Таск `extract_and_load_raw_data` запускає
  `data_generator.py` і `load_to_dwh.py` через `subprocess` у venv `etl`.
* Метадані Airflow зберігаються в SQLite (том `airflow_data`), виконавець — `SequentialExecutor`; для навчального проєкту цього достатньо.
* `retries: 1`, `retry_delay: 1 хв` — у разі збою таск автоматично перезапускається один раз.
* Розклад `@daily`, `catchup=False`.

## Структура репозиторію
```
.
├── docker-compose.yml   # PostgreSQL, Airflow, одноразові контейнери data_loader і dbt
├── Dockerfile           # образ Python для скриптів
├── Dockerfile.dbt       # образ dbt (dbt-core 1.8.8 + dbt-postgres 1.8.2)
├── Dockerfile.airflow   # образ Airflow 2.10.5 + venv для скриптів і dbt (ЛР №3)
├── airflow/dags/
│   └── autoparts_pipeline.py   # DAG autoparts_elt_pipeline (ЛР №3)
├── autoparts_dbt/       # dbt-проєкт (ЛР №2); staging/schema.yml — тести (ЛР №3)
├── images/              # скріншоти результатів (Airflow Graph, Metabase, Lineage)
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
