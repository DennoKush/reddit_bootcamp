import os
import sys
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts import transform_data, load_data

# Define default args for the DAG
default_args = {
    'owner': 'reddithackathon',
    'depends_on_past': False,
    'start_date': days_ago(0),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'reddit_etl',
    default_args=default_args,
    description='Reddit ETL Pipeline',
    schedule_interval=timedelta(hours=48),
)

# Extract Task: Fetch Reddit data and pass it using XCom
def extract_reddit_data(**kwargs):
    # Assuming main function fetches data from Reddit and returns it as a dictionary
    from scripts.extract_data import main as fetch_data
    all_data = fetch_data()
    
    # Push the fetched data to XCom
    return all_data

# Transform Task: Transforms the extracted data
def transform_reddit_data(**kwargs):
    ti = kwargs['ti']  # Task instance to pull data
    raw_data = ti.xcom_pull(task_ids='extract_reddit_data')  # Pull data from XCom
    transformed_data = []

    for key in raw_data:
        for post in raw_data[key]['hot']:
            transformed = transform_data.transform_data(post)
            transformed_data.append(transformed)
    
    # Return transformed data to XCom
    return transformed_data

# Load Task: Loads transformed data into PostgreSQL
def load_transformed_data(**kwargs):
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_reddit_data')  # Pull data from XCom
    for post in transformed_data:
        load_data.load_data(post)

# Define the PythonOperators
extract_task = PythonOperator(
    task_id='extract_reddit_data',
    python_callable=extract_reddit_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_reddit_data',
    python_callable=transform_reddit_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data_to_warehouse',
    python_callable=load_transformed_data,
    provide_context=True,
    dag=dag,
)

# Task dependencies
extract_task >> transform_task >> load_task
