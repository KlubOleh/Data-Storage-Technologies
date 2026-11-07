import os
import subprocess
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Шляхи (у контейнері значення за замовчуванням коректні; env-змінні потрібні лише для тестів)
SCRIPTS_DIR = os.getenv("ETL_SCRIPTS_DIR", "/opt/airflow/scripts")
WORK_DIR = os.getenv("ETL_WORK_DIR", "/opt/airflow/work")
ETL_PYTHON = os.getenv("ETL_PYTHON", "/home/airflow/venvs/etl/bin/python")
DBT_BIN = os.getenv("DBT_BIN", "/home/airflow/venvs/dbt/bin/dbt")
DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt/autoparts_dbt")
DBT_PROFILES_DIR = DBT_PROJECT_DIR  # profiles.yml лежить усередині dbt-проєкту

default_args = {
    "owner": "data_engineer",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,                         # одна повторна спроба у разі помилки
    "retry_delay": timedelta(minutes=1),
}


def extract_and_load():
    """Extract & Load (ЛР №1): генерація даних і завантаження їх у схему raw."""
    os.makedirs(WORK_DIR, exist_ok=True)
    for script in ("data_generator.py", "load_to_dwh.py"):
        print(f"Запуск {script}...")
        result = subprocess.run(
            [ETL_PYTHON, os.path.join(SCRIPTS_DIR, script)],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(f"{script} завершився з помилкою (код {result.returncode})")


# dbt пише службові файли у /tmp, щоб не залежати від прав доступу до змонтованої папки проєкту
DBT_ENV = {"DBT_TARGET_PATH": "/tmp/dbt_target", "DBT_LOG_PATH": "/tmp/dbt_logs"}

with DAG(
    dag_id="autoparts_elt_pipeline",
    default_args=default_args,
    description="Конвеєр завантаження, трансформації та перевірки даних магазину автозапчастин",
    schedule="@daily",       # щодня опівночі
    catchup=False,           # не запускати за минулі дати
    tags=["autoparts", "elt"],
) as dag:

    # Task 1: Extract & Load (ЛР №1)
    extract_load_task = PythonOperator(
        task_id="extract_and_load_raw_data",
        python_callable=extract_and_load,
    )

    # Task 2: Transform — dbt run (ЛР №2)
    dbt_run_task = BashOperator(
        task_id="dbt_run_transformations",
        bash_command=f"{DBT_BIN} run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
        env=DBT_ENV,
        append_env=True,
    )

    # Task 3: Data Quality Gate — dbt test
    dbt_test_task = BashOperator(
        task_id="dbt_test_task",
        bash_command=f"{DBT_BIN} test --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
        env=DBT_ENV,
        append_env=True,
    )

    # Послідовність: тести стартують ТІЛЬКИ після успішної трансформації
    extract_load_task >> dbt_run_task >> dbt_test_task
