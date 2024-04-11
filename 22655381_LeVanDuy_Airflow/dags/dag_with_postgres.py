import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.utils.trigger_rule import TriggerRule
from airflow.decorators import task, task_group

locals_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    'owner': 'duy',
    'start_date': datetime(2024, 1, 1, tzinfo=locals_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
}

with DAG(
    dag_id='dag_with_posgres_v02',
    default_args=default_args,
    schedule_interval="0 0 * * *",
    catchup=False,
) as dag:
    start = EmptyOperator(task_id="start")

    task_1 = PostgresOperator(
        task_id="create_postgres_table",
        postgres_conn_id="postgres_localhost",
        sql="""
            create table if not exists my_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                sex VARCHAR(10)
            )
        """
    )

    task_2 = PostgresOperator(
        task_id="insert_data_to_postgres_table",
        postgres_conn_id="postgres_localhost",
        sql="""
                INSERT INTO my_table (name, sex)
                VALUES ('John', 'Male'),
                       ('Jane', 'Female'),
                       ('Alex', 'Male')
            """
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start >> task_1 >> task_2 >> end


