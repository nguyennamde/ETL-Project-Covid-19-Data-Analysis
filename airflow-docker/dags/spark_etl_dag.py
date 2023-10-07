from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.utils.dates import days_ago
import datetime as dt

default_args = {
    "owner" : "nguyennam",
    "start_date" : days_ago(1),
    "email" : ["nguyennam250303@gmail.com"],
    "email_on_failure" : False,
    "email_on_retry" : False,
    "retries" : 1,
    "retry_delay" : dt.timedelta(minutes=5),
    "catchup" : True,
    "depends_on_past" : True
}

dag = DAG(dag_id="ETL_pipeline",
          default_args=default_args,
          schedule_interval="@daily")


ETL_task  = SparkSubmitOperator(task_id="ETL_to_DataWarehouse",
                                conn_id="spark_standalone",
                                application="/opt/airflow/dags/spark_etl.py",
                                dag=dag
                                )

ETL_task



