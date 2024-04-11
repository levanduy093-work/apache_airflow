import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
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
    dag_id='dag_with_task_group_v01',
    default_args=default_args,
    schedule_interval="0 0 * * *",
    catchup=True
) as dag:
    start = EmptyOperator(task_id="start")

    @task_group()
    def task_group_1():
        EmptyOperator(task_id="task_1") >> [EmptyOperator(task_id="task_2"), 
                                            EmptyOperator(task_id="task_3")]

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start >> task_group_1() >> end