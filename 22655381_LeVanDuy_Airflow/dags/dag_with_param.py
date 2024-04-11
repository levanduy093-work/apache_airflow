import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator
from airflow.decorators import task, task_group

locals_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    'owner': 'duy',
    'start_date': datetime(2024, 1, 1, tzinfo=locals_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
}

def with_param(name, age, address):
    print(f"Hello Everyone, my name is {name}, I'm {age} years old, and I'm living in {address}")

with DAG(
    dag_id='dag_with_param',
    default_args=default_args,
    params={
        "name": "duy",
        "age": 20,
        "address": "Go Vap, Ho Chi Minh City"
    }
) as dag:
    start = EmptyOperator(task_id="start")

    print_string_task = PythonOperator( 
        task_id="print_string_task",
        python_callable=with_param,
        op_kwargs={
            "name": "{{ params.name }}",
            "age": "{{ params.age }}",
            "address": "{{ params.address }}"
        }
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start >> print_string_task >> end