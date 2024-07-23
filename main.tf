terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
    helm = {
      source = "hashicorp/helm"
    }
  }
}

provider "kubernetes" {
  config_context = "minikube"
  config_path    = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = "minikube"
  }
}

#-------------------------------------------------------------
#                             AIRFLOW
#-------------------------------------------------------------

resource "kubernetes_namespace" "airflow_ns" {
  metadata {
    name = "airflow"
  }
}

resource "kubernetes_secret" "airflow_ssh_secret" {
  metadata {
    name      = "airflow-ssh-secret"
    namespace = "airflow"
  }

  data = {
    gitSshKey = file("~/.ssh/id_e25519_github")
  }

  type       = "Opaque"
  depends_on = [kubernetes_namespace.airflow_ns]
}

resource "helm_release" "airflow" {
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  name       = "airflow"
  version    = "1.14.0"
  namespace  = "airflow"

  values = [
    file("${path.root}/airflow_src/values.yaml")
  ]
  depends_on = [kubernetes_secret.airflow_ssh_secret]
}

resource "kubernetes_cluster_role_binding" "airflow_worker" {
  metadata {
    name = "airflow-worker"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  subject {
    kind      = "ServiceAccount"
    name      = "airflow-worker"
    namespace = "airflow"
  }
  depends_on = [helm_release.airflow]
}

#-------------------------------------------------------------
#                             SPARK
#-------------------------------------------------------------

resource "kubernetes_namespace" "spark_ns" {
  metadata {
    name = "spark-operator"
  }
}

resource "helm_release" "spark_operator" {
  repository = "https://kubeflow.github.io/spark-operator"
  chart      = "spark-operator"
  name       = "spark-operator"
  namespace  = "spark-operator"

  set {
    name  = "webhook.enable"
    value = "true"
  }

  set {
    name  = "webhook.namespaceSelector"
    value = "spark-webhook-enabled=true"
  }

  depends_on = [kubernetes_namespace.spark_ns]
}

