import os
import random

import pandas as pd
from faker import Faker

fake = Faker("uk_UA")
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = "data_lake"


def generate_manufacturers():
    print("Генерація виробників...")
    items = [
        ("Bosch", "Німеччина"),
        ("Brembo", "Італія"),
        ("Denso", "Японія"),
        ("Valeo", "Франція"),
        ("Mann-Filter", "Німеччина"),
        ("NGK", "Японія"),
        ("Sachs", "Німеччина"),
        ("Gates", "США"),
        ("Monroe", "США"),
        ("TRW", "Німеччина"),
        ("Luk", "Німеччина"),
        ("Hella", "Німеччина"),
    ]
    return pd.DataFrame(
        [
            {"manufacturer_id": i + 1, "manufacturer_name": n, "country": c}
            for i, (n, c) in enumerate(items)
        ]
    )


PART_CATALOG = {
    "Гальмівна система": ["Гальмівні колодки", "Гальмівний диск", "Гальмівний шланг", "Супорт"],
    "Фільтри": ["Масляний фільтр", "Повітряний фільтр", "Салонний фільтр", "Паливний фільтр"],
    "Підвіска": ["Амортизатор", "Стабілізатор", "Пружина підвіски", "Сайлентблок"],
    "Двигун": ["Свічка запалювання", "Ремінь ГРМ", "Помпа охолодження", "Прокладка ГБЦ"],
    "Електрика": ["Акумулятор", "Стартер", "Генератор", "Лампа H7"],
    "Трансмісія": ["Зчеплення (комплект)", "Півось", "ШРУС", "Масло трансмісійне"],
}


def generate_parts(n, manufacturer_ids):
    print(f"Генерація {n} запчастин...")
    data = []
    for i in range(1, n + 1):
        category = random.choice(list(PART_CATALOG))
        base_name = random.choice(PART_CATALOG[category])
        data.append({
            "part_id": i,
            "manufacturer_id": random.choice(manufacturer_ids),
            "part_name": f"{base_name} {fake.bothify('??-####').upper()}",
            "category": category,
            "price": round(random.uniform(50.0, 15000.0), 2),
            "is_active": random.choice([True, True, True, False]),
        })
    return pd.DataFrame(data)


CAR_BRANDS = [
    "Volkswagen", "Skoda", "Toyota", "Renault", "Opel", "BMW",
    "Audi", "Ford", "Honda", "Hyundai", "Kia", "Mazda"
]


def generate_car_owners(n):
    print(f"Генерація {n} власників авто (з 'брудними' даними)...")
    data = []
    for i in range(1, n + 1):
        data.append({
            "owner_id": i,
            "full_name": fake.name(),
            "email": fake.email() if random.random() > 0.1 else None,
            "phone": fake.phone_number(),
            "city": fake.city(),
            "car_brand": random.choice(CAR_BRANDS),
            "car_year": random.randint(1998, 2024),
            "registration_date": fake.date_between(start_date="-2y", end_date="today"),
        })
    df = pd.DataFrame(data)
    duplicates = df.sample(frac=0.05, random_state=42)
    return pd.concat([df, duplicates], ignore_index=True)


def generate_sales(n, owner_ids, parts_df):
    print(f"Генерація {n} продажів...")
    prices = dict(zip(parts_df["part_id"], parts_df["price"]))
    part_ids = parts_df["part_id"].tolist()
    data = []
    for _ in range(n):
        part_id = random.choice(part_ids)
        data.append({
            "sale_id": fake.uuid4(),
            "owner_id": random.choice(owner_ids),
            "part_id": part_id,
            "sale_date": fake.date_time_between(start_date="-1y", end_date="now"),
            "quantity": random.randint(1, 4),
            "unit_price": prices[part_id],
            "payment_method": random.choices(["card", "cash", "online"], weights=[50, 20, 30])[0],
        })
    return pd.DataFrame(data)


RETURN_REASONS = ["Брак", "Не підійшла до авто", "Передумав", "Пошкоджено при доставці", "Невірна комплектація"]


def generate_returns(n, sales_df):
    """Повернення пов'язані з реально існуючими продажами (ссилочна цілісність)."""
    print(f"Генерація {n} повернень...")
    sampled = sales_df.sample(n=n, random_state=42)
    data = []
    for _, s in sampled.iterrows():
        qty = random.randint(1, int(s["quantity"]))
        data.append({
            "return_id": fake.uuid4(),
            "sale_id": s["sale_id"],
            "owner_id": s["owner_id"],
            "part_id": s["part_id"],
            "return_date": s["sale_date"] + pd.Timedelta(days=random.randint(1, 30)),
            "quantity": qty,
            "refund_amount": round(qty * s["unit_price"], 2),
            "reason": random.choice(RETURN_REASONS),
            "comment": fake.sentence(nb_words=10) if random.random() > 0.2 else None,
        })
    return pd.DataFrame(data)


def generate_reviews(n, parts_df, owner_ids):
    """
    Генерація відгуків на товари згідно з ТЗ до лабораторної роботи:
    поля review_id, product_id, user_id, rating (1-5) та comment (20% NULL).
    """
    print(f"Генерація {n} відгуків...")
    part_ids = parts_df["part_id"].tolist()
    data = []
    for _ in range(n):
        data.append({
            "review_id": fake.uuid4(),
            "product_id": random.choice(part_ids),
            "user_id": random.choice(owner_ids),
            "rating": random.randint(1, 5),
            "comment": fake.sentence(nb_words=8) if random.random() > 0.2 else None,
        })
    return pd.DataFrame(data)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Починаємо генерацію даних...")

    df_manufacturers = generate_manufacturers()
    df_parts = generate_parts(150, df_manufacturers["manufacturer_id"].tolist())
    df_owners = generate_car_owners(600)
    unique_owner_ids = df_owners["owner_id"].unique().tolist()
    df_sales = generate_sales(5000, unique_owner_ids, df_parts)
    df_returns = generate_returns(400, df_sales)
    df_reviews = generate_reviews(800, df_parts, unique_owner_ids)

    tables = {
        "manufacturers": df_manufacturers,
        "parts": df_parts,
        "car_owners": df_owners,
        "sales": df_sales,
        "returns": df_returns,
        "reviews": df_reviews,
    }
    for name, df in tables.items():
        df.to_parquet(f"{OUTPUT_DIR}/raw_{name}.parquet", index=False)
        print(f"  raw_{name}.parquet: {len(df)} рядків")
    print(f"Генерація завершена. Файли збережено у /{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
