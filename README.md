# MLflow + OAuth2 Proxy + Keycloak on Kubernetes

This project provides a complete setup for deploying [MLflow](https://mlflow.org/) with Keycloak-based authentication using [`oauth2-proxy`](https://oauth2-proxy.github.io/oauth2-proxy/) on a local Kubernetes cluster (e.g. Minikube). Helm is used to manage deployments.

---

## Components

- **MLflow** — For tracking machine learning experiments.
- **OAuth2 Proxy** — Protects MLflow UI and integrates with Keycloak.
- **Keycloak** — Identity Provider (external to this chart, must be configured separately).
- **Helm** — Deployment management.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/)
- A working **Keycloak** instance with:
    - A **realm**
    - A **client** named `mlflow-client`
    - Redirect URI: `http://localhost:4180/oauth2/callback`
    - Client Secret
    - At least one user created and assigned to the realm

---

## Quickstart

### 1. Start Minikube

```bash
minikube start --cpus 4 --memory 8192 --driver=docker
```
### 2. Create the Namespace

```bash
kubectl create namespace mlflow-auth-helm
```
### 3. Deploy MLflow + OAuth2 Proxy

From this Helm chart directory:
```bash
helm dependency update .
helm install mlflow-auth . -n mlflow-auth-helm
```
### Accessing MLflow
Forward the port:
```bash
kubectl port-forward svc/oauth2-proxy-service 4180:4180 -n mlflow-auth-helm
```

further: Verifying the deployment:
```bash
kubectl get pods -n mlflow-auth-helm
kubectl logs -n mlflow-auth-helm deployment/mlflow
kubectl logs -n mlflow-auth-helm deployment/oauth2-proxy
```