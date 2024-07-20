import os
from airflow.models.connection import Connection
from airflow import settings

conn = Connection(
    conn_id="S3",
    conn_type="aws",
    login="AKIA2N3NJHZEIXFGLVIK",  # Reference to AWS Access Key ID
    password="KBV4sHFfslKuMg14DGpcJMlf+MCqCUKOeVO335Mc",  # Reference to AWS Secret Access Key
    extra={
        # Specify extra parameters here
        "region_name": "us-east-1",
        "endpoint_url": "https://s3.us-east-1.amazonaws.com"
    },
)

# Generate Environment Variable Name and Connection URI
env_key = f"AIRFLOW_CONN_{conn.conn_id.upper()}"
conn_uri = conn.get_uri()
print(f"{env_key}={conn_uri}")
# AIRFLOW_CONN_SAMPLE_AWS_CONNECTION=aws://AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI%2FK7MDENG%2FbPxRfiCYEXAMPLEKEY@/?region_name=eu-central-1

os.environ[env_key] = conn_uri
print(conn.test_connection())  # Validate connection credentials.
if conn.test_connection()[0]:
    session = settings.Session() # get the session
    session.add(conn)
    session.commit()
    print("Connection successful.")
    