# Production Kubernetes Deployment Manifests

This directory contains the complete Kubernetes production manifests for the **NeuralForge Cluster Admin** stack (`wyoloservice2_cluster_control`), split into isolated microservice components:

## Components

1. **`api/` (Cluster Admin API Backend)**
   * Role-Based Access Control (RBAC) with scoped `ServiceAccount` and `Role` for Pod inspection and signal delivery.
   * `ConfigMap` and secure `Secret` template with generic placeholders.
   * RollingUpdate `Deployment` with liveness/readiness probes.
   * `Service` (ClusterIP: 8001) and NGINX `Ingress` mapping `/api/v1` and `/health`.

2. **`interfaz/` (Cluster Admin UI Frontend)**
   * `ConfigMap` providing runtime configuration (`CLUSTER_API_URL`).
   * RollingUpdate `Deployment` for the VSCode Workbench SPA running `cluster_admin_ui_v3.2.3`.
   * `Service` (ClusterIP: 8501) and NGINX `Ingress` mapping root traffic `/`.

## Key Technologies and Libraries
* **Orchestrator:** Kubernetes 1.28+ (Namespace: `train-service`)
* **Ingress Controller:** Ingress-NGINX
* **Images:** `wisrovi/train_service:cluster_admin_api_v3.2.3`, `wisrovi/train_service:cluster_admin_ui_v3.2.3`
* **Configuration:** Kubernetes ConfigMaps, Secrets, RBAC RoleBindings

## Deploying the Entire Stack

```bash
# 1. Deploy API backend
kubectl apply -f api/

# 2. Deploy UI frontend
kubectl apply -f interfaz/
```
