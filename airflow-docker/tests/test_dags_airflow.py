import sys
import pandas as pd
from spark_etl import *
import pytest
from airflow.models import DagBag
import airflow
sys.path.append("/opt/airflow")


@pytest.fixture() 
def dag():
    return DagBag(dag_folder="/opt/airflow/dags", include_examples=False).\
        get_dag(dag_id="ETL_pipeline")

## DAG Tests
# test #1 - dag loaded
def test_dag_loaded(dag):
    assert dag is not None

# test #2 - dag contains 2 tasks
def test_task_count(dag):
    assert len(dag.tasks) == 1

# test #3 - test task ids
def test_contain_tasks(dag):
    task_ids = list(map(lambda task: task.task_id, dag.tasks))
    assert "ETL_to_DataWarehouse" in task_ids

