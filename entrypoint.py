import os
import time
import subprocess
import sys

import psycopg2


def wait_for_db():
    host = os.environ.get("DB_HOST", "db")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "product_inventory")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "password")

    print("Waiting for PostgreSQL...")
    for i in range(30):
        try:
            conn = psycopg2.connect(
                dbname=name,
                user=user,
                password=password,
                host=host,
                port=port,
            )
            conn.close()
            print("PostgreSQL is ready.")
            return
        except Exception as exc:
            print(f"Waiting... ({i + 1}/30) {exc}")
            time.sleep(2)
    raise SystemExit("PostgreSQL did not become ready in time.")


def main():
    wait_for_db()
    subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])
    subprocess.check_call(
        [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    )


if __name__ == "__main__":
    main()
