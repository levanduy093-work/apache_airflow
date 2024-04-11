import pendulum
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.utils.trigger_rule import TriggerRule
from airflow.hooks.postgres_hook import PostgresHook # type: ignore

locals_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    'owner': 'Le Van Duy',
    'start_date': datetime(2024, 1, 1, tzinfo=locals_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': True,
}

def print_task1():
    print('Cong viec 1')

def process_data():
    df = pd.read_csv('/opt/airflow/include/dataset/online_retail.csv')
    df = df.dropna()
    return df

def save_data():
    df = process_data()
    # Lưu DataFrame vào một tệp CSV mới
    df.to_csv('/opt/airflow/include/dataset/processed_online_retail.csv', index=False)

def load_data():
    pg_hook = PostgresHook(postgres_conn_id='postgres_localhost')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    with open('/opt/airflow/include/dataset/online_retail.csv', 'r') as f:
        cursor.copy_expert("COPY online_retail FROM STDIN WITH CSV HEADER", f)
    conn.commit()


with DAG(
    dag_id='22655381_DAG2',
    default_args=default_args,
    schedule_interval='* * * * *',
    catchup=False,
) as dag:
    task_1 = PythonOperator(
        task_id='print_task_1',
        python_callable=print_task1,
    )

    task_2 = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )

    task_3 = PythonOperator(
        task_id='save_data',
        python_callable=save_data,
    )

    task_4 = PostgresOperator(
        task_id='create_table',
        sql='''CREATE TABLE IF NOT EXISTS online_retail (
            InvoiceNo VARCHAR(10),
            StockCode VARCHAR(50),
            Description TEXT,
            Quantity INT,
            InvoiceDate TIMESTAMP,
            UnitPrice FLOAT,
            CustomerID INT,
            Country VARCHAR(50)
        )''',
        postgres_conn_id='postgres_localhost',
    )

    task_5 = PythonOperator(
        task_id='insert_data',
        python_callable=load_data,
        dag=dag,
    )

    task_1 >> task_2 >> task_3 >> task_4 >> task_5
