# Cluster Admin UI Kubernetes Manifests (Production)

Production Kubernetes deployment manifests for `cluster_admin_ui` (VSCode Workbench SPA interface served via Python lightweight HTTP server).

> [!NOTE]
> Unlike Streamlit and Gradio dashboards which have strict websocket/session affinity considerations, `cluster_admin_ui` operates as an ultra-fast, stateless VSCode Workbench SPA connecting dynamically to `cluster-admin-api` via `/config.js`.

## Key Technologies and Libraries
*   **Kubernetes Workloads:** Deployments, ClusterIP Services, NGINX Ingress Controller.
*   **Frontend Runtime:** Lightweight Python HTTP static server with dynamic runtime `/config.js` injection.
*   **Networking:** NGINX reverse proxy with extended keep-alive and proxy timeouts.

## Manifest Layout
*   `01-config.yaml`: ConfigMap (`cluster-admin-ui-config`) pointing to backend API service.
*   `02-deployment.yaml`: RollingUpdate Deployment running `wisrovi/train_service:cluster_admin_ui_v3.2.3` with liveness and readiness health checks.
*   `03-service-ingress.yaml`: ClusterIP service exposing port 8501 and NGINX Ingress controller configuration.

## Deployment Steps
1. Apply the manifests:
   ```bash
   kubectl apply -f 01-config.yaml
   kubectl apply -f 02-deployment.yaml
   kubectl apply -f 03-service-ingress.yaml
   ```
2. Check rollout status:
   ```bash
   kubectl rollout status deployment/cluster-admin-ui -n train-service
   ```
