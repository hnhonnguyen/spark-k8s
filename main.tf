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
#                             ARGOCD
#-------------------------------------------------------------

resource "kubernetes_namespace" "argocd_ns" {
  metadata {
    name = "argocd"
  }
}

data "http" "argocd_manifest" {
  url = "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
}

resource "kubectl_manifest" "argocd" {
  yaml_body          = data.http.argocd_manifest
  override_namespace = "argocd"
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

resource "kubernetes_cluster_role" "full_access_role" {
  metadata {
    name = "full-access-role"
  }

  rule {
    api_groups = ["*"]
    resources  = ["*"]
    verbs      = ["*"]
  }
}

resource "kubernetes_cluster_role_binding" "full_access_binding" {
  metadata {
    name = "full-access-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.full_access_role.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = "spark-operator"
    namespace = "spark-operator"
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
    name  = "webhook.port"
    value = "443"
  }

  depends_on = [kubernetes_namespace.spark_ns]
}

