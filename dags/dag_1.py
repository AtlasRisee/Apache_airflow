from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'count_a',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

def create_files(**kwargs):
    import string
    import random
    for i in range(100):
        with open(f'/tmp/file_{i}.txt', 'w') as f:
            f.write(''.join(random.choice(string.ascii_letters) for _ in range(100)))

def count_a(**kwargs):
    import subprocess
    results = []
    for i in range(100):
        with open(f'/tmp/file_{i}.txt', 'r') as f:
            text = f.read()
            count = text.count('a')
            with open(f'/tmp/file_{i}.res', 'w') as res:
                res.write(str(count))
            results.append(count)
    return results

def sum_results(**kwargs):
    results = kwargs['task_instance'].xcom_pull(task_ids='count_a')
    sum_count = sum(results)
    with open('/tmp/result.txt', 'w') as f:
        f.write(str(sum_count))
    print('Кол-во букв ''а'':' + str(sum_count))

create_files_task = PythonOperator(
    task_id='create_files',
    python_callable=create_files,
    dag=dag,
)

count_a_task = PythonOperator(
    task_id='count_a',
    python_callable=count_a,
    dag=dag,
)

sum_results_task = PythonOperator(
    task_id='sum_results',
    python_callable=sum_results,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_task',
    trigger_rule='all_done',
    dag=dag,
)

create_files_task >> count_a_task >> sum_results_task >> end_task