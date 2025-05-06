# MLflow + OAuth2 Proxy + Keycloak on Kubernetes

This project provides a complete setup for deploying [MLflow](https://mlflow.org/) with Keycloak-based authentication using [`oauth2-proxy`](https://oauth2-proxy.github.io/oauth2-proxy/) on a local Kubernetes cluster (e.g. Minikube). Helm is used to manage deployments.

---

## Components

- **MLflow** — For tracking machine learning experiments.
- **OAuth2 Proxy** — Protects MLflow UI and integrates with Keycloak.
- **Keycloak** — Identity Provider (external to this chart, must be configured separately).
- **PostgreSQL** — Persistent database backend for MLflow (running on port 5443).
- **Helm** — Deployment management.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/)
- [Python 3.8+](https://www.python.org/downloads/) (for running test scripts)
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

### 4. Test the PostgreSQL Database Connection

To verify that MLflow can connect to the PostgreSQL database, follow these steps:

1. First, create a Python virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set up port forwarding for PostgreSQL (running on port 5443):
```bash
kubectl port-forward -n mlflow-auth-helm mlflow-auth-postgresql-0 5443:5443
```

3. In a new terminal, run the test script:
```bash
source .venv/bin/activate
python test-mlflow-db.py --tracking-uri postgresql://mlflow:mlflow-password@localhost:5443/mlflow
```

The test script will:
- Verify the PostgreSQL connection
- Create a test experiment
- Log a test metric
- Confirm that MLflow can interact with the database

A successful test will show:
```
✅ PostgreSQL connection successful!
PostgreSQL version: PostgreSQL 14.5 ...

Testing MLflow tracking with PostgreSQL...
MLflow Tracking URI: postgresql://mlflow:mlflow-password@localhost:5443/mlflow
Created new experiment: db-test-experiment (ID: 1)
✅ Successfully logged metric to run <run_id>

✅ All tests passed! MLflow is properly configured with PostgreSQL.
```

### Database Configuration Details

The PostgreSQL database is configured with:
- Port: 5443 (custom port to avoid conflicts)
- Database name: mlflow
- Username: mlflow
- Password: mlflow-password
- Persistence: 8Gi storage

The database configuration can be customized in `values.yaml` under the `postgresql` section.

### Accessing MLflow
Forward the port:
```bash
kubectl port-forward svc/oauth2-proxy-service 4180:4180 -n mlflow-auth-helm
```

### Verifying the Deployment
```bash
kubectl get pods -n mlflow-auth-helm
kubectl logs -n mlflow-auth-helm deployment/mlflow