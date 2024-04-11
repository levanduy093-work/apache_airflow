
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import BigQueryToGCSOperator

from airflow.utils.trigger_rule import TriggerRule

locals_tz = pendulum.timezone("Asia/Ho_Chi_Minh")
default_args = {
    'owner': 'duy',
    'start_date': datetime(2024, 1, 1, tzinfo=locals_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': False,
}

with DAG(
    dag_id='dag_with_gg_bigquery_v07',
    default_args=default_args,
    schedule_interval="0 0 * * *",
    catchup=False,
) as dag:
    start = EmptyOperator(task_id="start")

    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_csv_to_gcs',
        src='/opt/airflow/include/dataset/online_retail.csv', # Path to the file on the local filesystem
        dst='raw/online_retail.csv',
        bucket='airflow_online_retail_lab7', # Name of the bucket in GCS which you defined in the previous step
        gcp_conn_id='gcp',
        mime_type='text/csv',
    )

    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_dataset',
        dataset_id='retail',
        gcp_conn_id='gcp',
    )

    load_csv_to_bigquery = GCSToBigQueryOperator(
        task_id='load_csv_to_bigquery',
        bucket='airflow_online_retail_lab7',
        source_objects=['raw/online_retail.csv'],
        destination_project_dataset_table='retail.online_retail',
        source_format='CSV',
        skip_leading_rows=1,
        gcp_conn_id='gcp',
    )

    first_query = BigQueryExecuteQueryOperator(
        task_id='first_query',
        sql='''
            SELECT * FROM `retail.online_retail` LIMIT 1000
        ''',
        use_legacy_sql=False,
        gcp_conn_id='gcp',
    )

    query_and_store_result = BigQueryExecuteQueryOperator(
        task_id='query_and_store_result',
        sql='''
            CREATE OR REPLACE TABLE `retail.query_result` AS
            SELECT * FROM `retail.online_retail` LIMIT 1000
        ''',
        use_legacy_sql=False,
        gcp_conn_id='gcp',
    )

    export_query_result_to_gcs = BigQueryToGCSOperator(
        task_id='export_query_result_to_gcs',
        source_project_dataset_table='retail.query_result',
        destination_cloud_storage_uris=['gs://airflow_online_retail_lab7/result/query_result.csv'],
        export_format='CSV',
        gcp_conn_id='gcp',
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start >> upload_csv_to_gcs >> create_dataset >> load_csv_to_bigquery >> first_query >> query_and_store_result >> export_query_result_to_gcs >> end







