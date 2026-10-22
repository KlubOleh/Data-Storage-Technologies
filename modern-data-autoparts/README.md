# Data-Storage-Technologies[README.md](https://github.com/user-attachments/files/33542912/README.md)
# Modern Data Stack: Магазин автозапчастин (Варіант 5)

Навчальний проєкт з дисципліни «Технології сховищ даних» (НУ «Львівська політехніка», кафедра ЕОМ).
Повноцінний ELT-конвеєр: **Python → PostgreSQL (Docker) → dbt → Airflow → Metabase**.

> Поточний етап: **ЛР №1 — Data Ingestion (Extract & Load)**.

## Предметна область
Магазин автозапчастин.

| Таблиця | Тип | Опис |
|---|---|---|
| `manufacturers` | Dimension | Виробники запчастин |
| `parts` | Dimension | Запчастини (FK → manufacturers) |
| `car_owners` | Dimension | Власники авто (клієнти) |
| `sales` | **Fact** | Продажі (FK → car_owners, parts) |
| `returns` | **Fact** | Повернення (FK → sales, car_owners, parts) |

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

## Структура репозиторію
```
.
├── docker-compose.yml   # PostgreSQL + одноразовий контейнер data_loader
├── Dockerfile           # образ Python для скриптів
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
