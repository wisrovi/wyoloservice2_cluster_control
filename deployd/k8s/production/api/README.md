# Cluster Admin API Kubernetes Manifests (Production)

Production Kubernetes deployment manifests for `cluster_admin_api` (FastAPI backend service).

## Key Technologies and Libraries
*   **Kubernetes Workloads:** Deployments, ClusterIP Services, NGINX Ingress Controller.
*   **RBAC & Security:** Scoped ServiceAccounts and Roles for Kubernetes pod inspection and termination in `train-service` namespace.
*   **Backend Stack:** FastAPI, Pydantic, Redis client, Celery control client.

## Manifest Layout
*   `01-rbac.yaml`: ServiceAccount (`neuralforge-cluster-admin-sa`), Role and RoleBinding for monitoring pods and reading ConfigMaps.
*   `02-config.yaml`: ConfigMap (`cluster-admin-api-config`) and Secret template (`cluster-admin-api-secrets`).
*   `03-deployment.yaml`: RollingUpdate Deployment running `wisrovi/train_service:cluster_admin_api_v3.2.3` with liveness/readiness probes.
*   `04-service-ingress.yaml`: ClusterIP service exposing port 8001 and NGINX Ingress for external access.

## Deployment Steps
1. Configure credentials in `02-config.yaml` using generic placeholders or SealedSecrets:
   ```bash
   kubectl apply -f 01-rbac.yaml
   kubectl apply -f 02-config.yaml
   kubectl apply -f 03-deployment.yaml
   kubectl apply -f 04-service-ingress.yaml
   ```
2. Verify deployment status:
   ```bash
   kubectl get pods -n train-service -l app.kubernetes.io/name=cluster-admin-api
   ```
