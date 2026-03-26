from datetime import datetime
from io import BytesIO

import pandas as pd
from airflow.sdk import DAG, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


with DAG(
    dag_id="local_postgres_and_s3_demo",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["local", "demo"],
) as dag:

    @task
    def write_to_postgres():
        hook = PostgresHook(postgres_conn_id="app_postgres")
        hook.run("""
            CREATE TABLE IF NOT EXISTS demo_orders (
                id SERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                amount NUMERIC(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        hook.run("""
            INSERT INTO demo_orders (customer_name, amount)
            VALUES ('Jan Kowalski', 123.45);
        """)

    @task
    def upload_csv_to_s3():
        df = pd.DataFrame(
            [
                {"customer_name": "Jan Kowalski", "amount": 123.45},
                {"customer_name": "Anna Nowak", "amount": 88.90},
            ]
        )

        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        s3 = S3Hook(aws_conn_id="local_s3")
        bucket_name = "demo-bucket"

        if not s3.check_for_bucket(bucket_name):
            s3.create_bucket(bucket_name=bucket_name)

        s3.load_bytes(
            bytes_data=buffer.getvalue(),
            key="exports/orders.csv",
            bucket_name=bucket_name,
            replace=True,
        )

    write_to_postgres() >> upload_csv_to_s3()
