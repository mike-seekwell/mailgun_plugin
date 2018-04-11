"""
An example DAG using the Mailgun plugin.
"""

from datetime import datetime, timedelta

from airflow import DAG

# from airflow.plugins.mailgun_plugin import MailgunPlugin
# from airflow.plugins import mailgun_plugin
# from airflow.sensors import ToySensorOperator
# from plugins.sensors import ToySensorOperator

# from airflow.hooks import MailgunHook
# from airflow.operators.sensors import EmailListChangedSensor
from airflow.operators import EmailListChangedSensor
from airflow.operators import EmailValidationOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 4, 6),
    'email': 'taylor@astronomer.io',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=0),
}

dag = DAG(
    "mailgun_dag",
    default_args=default_args,
    schedule_interval='@once',
)

start = DummyOperator(
    task_id='start',
    dag=dag,
)

emails_changed = EmailListChangedSensor(
    task_id='email_list_delta_sensor',
    poke_interval=0,
    timeout=0,
    soft_fail=True,
    dag=dag,
)
emails_changed.set_upstream(start)

email_validation_operator = EmailValidationOperator(
    task_id='validate_emails',
    mailgun_conn_id='mailgun_api',

    aws_conn_id='aws_s3',
    s3_bucket_name='astronomer-workflows-dev',
    s3_key_source='astronomer/pardot/list_50674.json',

    dag=dag,
)
email_validation_operator.set_upstream(emails_changed)
