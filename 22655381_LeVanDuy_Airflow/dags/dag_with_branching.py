import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.decorators import task, task_group

local_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    'owner': 'duy',
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
}

@task.branch(task_id="branching")
def task_branching():
    return "task_1"

with DAG(
    dag_id='dag_with_branching',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    catchup=True,
) as dag:
    start = EmptyOperator(task_id="start")

    branch = task_branching()

    task_1 = EmptyOperator(task_id="task_1")
    task_2 = EmptyOperator(task_id="task_2")

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start >> branch >> [task_1, task_2] >> end