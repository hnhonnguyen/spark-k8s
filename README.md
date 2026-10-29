# Spark on Kubernetes — local lab

A self-contained lab that runs a PySpark ETL pipeline on a local Kubernetes
cluster (minikube), with ArgoCD as the deployment layer and Airflow / cron jobs
as the scheduler.

## What's here

| Path | Purpose |
| --- | --- |
| `main.tf`, `version.tf` | Terraform: installs ArgoCD via Helm, creates the `airflow` namespace, the Git SSH secret, and a worker RBAC binding |
| `spark-operator-argocd-app.yaml` | ArgoCD Application installing the Kubeflow Spark Operator chart (webhook enabled) |
| `airflow-argocd-app.yaml` | ArgoCD Application for Airflow |
| `airflow_src/values.yaml` | Helm values used by the Airflow application |
| `src/etl.py` | PySpark ETL job |
| `src/insert_rows.py` | Loads rows into Postgres |
| `src/dockerfile`, `src/dockerfile-airflow`, `src/insertDockerfile` | Images for the jobs |
| `src/cronjob-etl.yaml`, `src/cronjob-insert-rows.yaml` | CronJobs running the pipeline on a schedule |
| `src/spark-app.yaml`, `src/etl-pod.yaml` | Spark application and pod manifests |
| `src/spark-service-role.yaml` | ServiceAccount/RBAC for the Spark driver |
| `src/postgres`, `src/cm-db.yaml`, `src/createS3connection.py` | Postgres deployment and connection setup |

## How it fits together

minikube → Terraform installs ArgoCD → ArgoCD deploys the Spark Operator and
Airflow → scheduled jobs submit PySpark work → results land in Postgres.

## Prerequisites

- minikube (context name `minikube`), `kubectl`, `terraform >= 1.0`, Docker
- A Spark Operator namespace created by the ArgoCD app (`spark-operator`)

## Usage

```bash
minikube start

terraform init
terraform apply

kubectl apply -f spark-operator-argocd-app.yaml
kubectl apply -f airflow-argocd-app.yaml

# build the job images inside minikube's Docker daemon
eval "$(minikube docker-env)"
docker build -t my-etl-container -f src/dockerfile src
# build the insert job image the same way (see src/cronjob-insert-rows.yaml for its name)

kubectl apply -f src/cm-db.yaml
kubectl apply -f src/cronjob-etl.yaml
```

## Notes

- The Kubernetes/Helm providers are pinned to the `minikube` context and read
  `~/.kube/config`, and the Airflow SSH secret reads
  `~/.ssh/id_e25519_github` — adjust both for your machine.
- This lab targets a local cluster. For a managed version on AWS see
  [`eks-data-platform`](https://github.com/hnhonnguyen/eks-data-platform).
