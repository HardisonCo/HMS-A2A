# CI/CD Pipeline Implementation

This document provides detailed instructions for setting up the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Crohn's Treatment System. It includes configuration files, step-by-step setup instructions, and best practices.

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [GitHub Actions Configuration](#github-actions-configuration)
3. [Docker Configuration](#docker-configuration)
4. [Kubernetes Configuration](#kubernetes-configuration)
5. [Pipeline Security](#pipeline-security)
6. [Integration with Third-Party Services](#integration-with-third-party-services)
7. [Testing in the Pipeline](#testing-in-the-pipeline)
8. [Deployment Environments](#deployment-environments)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Pipeline Troubleshooting](#pipeline-troubleshooting)

## Pipeline Overview

The CI/CD pipeline for the Crohn's Treatment System automates building, testing, and deploying the application across multiple environments. The pipeline is implemented using GitHub Actions and integrates with AWS services for deployment.

### Pipeline Architecture

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  Push to  │────►│  Run      │────►│  Build    │────►│  Scan     │
│  GitHub   │     │  Tests    │     │  Images   │     │  Security │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
                                                            │
┌───────────┐     ┌───────────┐     ┌───────────┐          │
│  Monitor  │◄────┤  Deploy   │◄────┤  Push     │◄─────────┘
│  Health   │     │  to Env   │     │  Images   │
└───────────┘     └───────────┘     └───────────┘
```

### Pipeline Flow

1. **Code Push**: Developer pushes code to GitHub repository
2. **Build & Test**: Pipeline builds the application and runs tests
3. **Container Build**: Docker images are built for each component
4. **Security Scan**: Container images are scanned for vulnerabilities
5. **Artifact Storage**: Images are pushed to Amazon ECR
6. **Deployment**: Application is deployed to the appropriate environment based on branch
7. **Validation**: Health checks and smoke tests verify deployment success
8. **Promotion**: Manual approval for promotion to higher environments

## GitHub Actions Configuration

### Main Workflow Configuration

Create a file at `.github/workflows/main.yml`:

```yaml
name: Crohns Treatment System CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Set up Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          components: rustfmt, clippy
      
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black isort
      
      - name: Lint Python code
        run: |
          flake8 src tests
          black --check src tests
          isort --check src tests
      
      - name: Lint Rust code
        run: |
          cd src/coordination/genetic-engine
          cargo fmt -- --check
          cargo clippy -- -D warnings

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Set up Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pytest-cov
      
      - name: Build Rust components
        run: |
          cd src/coordination/genetic-engine
          cargo build --release
      
      - name: Run Python tests
        run: |
          pytest --cov=src tests/ --cov-report=xml
      
      - name: Run Rust tests
        run: |
          cd src/coordination/genetic-engine
          cargo test
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' || github.event.pull_request.merged == true
    outputs:
      image: ${{ steps.build-image.outputs.image }}
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: crohns-treatment-system
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "::set-output name=image::$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
      
      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.build-image.outputs.image }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: development
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Deploy to Dev Environment
        uses: aws-actions/amazon-eks-update-kubeconfig@v1
        with:
          cluster-name: crohns-dev-cluster
          aws-region: us-west-2
      
      - name: Deploy to Kubernetes
        run: |
          sed -i "s|IMAGE_TO_REPLACE|${{ needs.build.outputs.image }}|g" kubernetes/dev/*.yaml
          kubectl apply -f kubernetes/dev/
      
      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/crohns-api-gateway -n crohns
          kubectl rollout status deployment/crohns-a2a-service -n crohns
          kubectl rollout status deployment/crohns-genetic-engine -n crohns
      
      - name: Run Smoke Tests
        run: |
          python tests/smoke/test_dev_deployment.py
  
  deploy-staging:
    needs: [build, deploy-dev]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Deploy to Staging Environment
        uses: aws-actions/amazon-eks-update-kubeconfig@v1
        with:
          cluster-name: crohns-staging-cluster
          aws-region: us-west-2
      
      - name: Deploy to Kubernetes
        run: |
          sed -i "s|IMAGE_TO_REPLACE|${{ needs.build.outputs.image }}|g" kubernetes/staging/*.yaml
          kubectl apply -f kubernetes/staging/
      
      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/crohns-api-gateway -n crohns
          kubectl rollout status deployment/crohns-a2a-service -n crohns
          kubectl rollout status deployment/crohns-genetic-engine -n crohns
      
      - name: Run Integration Tests
        run: |
          python tests/integration/test_staging_deployment.py
  
  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.crohns-treatment.example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Deploy to Production Environment
        uses: aws-actions/amazon-eks-update-kubeconfig@v1
        with:
          cluster-name: crohns-production-cluster
          aws-region: us-west-2
      
      - name: Deploy to Kubernetes
        run: |
          sed -i "s|IMAGE_TO_REPLACE|${{ needs.build.outputs.image }}|g" kubernetes/production/*.yaml
          kubectl apply -f kubernetes/production/
      
      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/crohns-api-gateway -n crohns
          kubectl rollout status deployment/crohns-a2a-service -n crohns
          kubectl rollout status deployment/crohns-genetic-engine -n crohns
      
      - name: Run Post-Deployment Tests
        run: |
          python tests/smoke/test_production_deployment.py
```

### Release Workflow

Create a file at `.github/workflows/release.yml`:

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Build and test
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pytest-cov
          pytest --cov=src tests/
      
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
          body: |
            Release ${{ github.ref }}
            
            Please refer to [CHANGELOG.md](https://github.com/organization/crohns-treatment-system/blob/main/CHANGELOG.md) for details.
      
      - name: Generate Release Notes
        run: |
          python scripts/generate_release_notes.py > release_notes.md
      
      - name: Update Release with Notes
        uses: actions/update-release-body@v1
        with:
          release-id: ${{ steps.create_release.outputs.id }}
          body-file: release_notes.md
```

## Docker Configuration

### Dockerfile for API Gateway

Create a file at `Dockerfile`:

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for building genetic-engine
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Copy Rust codebase
COPY src/coordination/genetic-engine /app/src/coordination/genetic-engine

# Build Rust genetic-engine
RUN cd /app/src/coordination/genetic-engine && \
    cargo build --release

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy Rust binary from builder stage
COPY --from=builder /app/src/coordination/genetic-engine/target/release/libgenetic_engine.so /app/lib/

# Copy application code
COPY src /app/src
COPY config /app/config
COPY scripts /app/scripts

# Set Python path and LD_LIBRARY_PATH
ENV PYTHONPATH=/app
ENV LD_LIBRARY_PATH=/app/lib

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; r = requests.get('http://localhost:8000/health'); exit(1) if r.status_code != 200 else exit(0);"

# Run the application
EXPOSE 8000
CMD ["python", "-m", "src.api_gateway.app"]
```

### Docker Compose for Development

Create a file at `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: crohns_treatment
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api-gateway:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/crohns_treatment
      REDIS_URL: redis://redis:6379/0
      A2A_SERVICE_URL: http://a2a-service:8001
      LOG_LEVEL: debug
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      a2a-service:
        condition: service_started
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./config:/app/config

  a2a-service:
    build:
      context: .
      dockerfile: Dockerfile.a2a
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/crohns_treatment
      REDIS_URL: redis://redis:6379/0
      GENETIC_ENGINE_URL: http://genetic-engine:8002
      LOG_LEVEL: debug
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8001:8001"
    volumes:
      - ./src:/app/src
      - ./config:/app/config

  genetic-engine:
    build:
      context: .
      dockerfile: Dockerfile.genetic-engine
    environment:
      LOG_LEVEL: debug
    ports:
      - "8002:8002"
    volumes:
      - ./src/coordination/genetic-engine:/app/src

  prometheus:
    image: prom/prometheus:v2.43.0
    volumes:
      - ./infrastructure/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:9.5.2
    depends_on:
      - prometheus
    ports:
      - "3002:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./infrastructure/grafana/provisioning:/etc/grafana/provisioning
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: "false"

volumes:
  postgres-data:
  prometheus-data:
  grafana-data:
```

## Kubernetes Configuration

### API Gateway Deployment

Create a file at `kubernetes/dev/api-gateway.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: crohns-api-gateway-config
  namespace: crohns
data:
  config.json: |
    {
      "logging": {
        "level": "info",
        "format": "json"
      },
      "cors": {
        "allowed_origins": ["*"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allowed_headers": ["*"],
        "expose_headers": ["Content-Length"],
        "max_age": 86400
      }
    }

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crohns-api-gateway
  namespace: crohns
  labels:
    app: crohns-api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crohns-api-gateway
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: crohns-api-gateway
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: "/metrics"
        prometheus.io/port: "8000"
    spec:
      containers:
      - name: api-gateway
        image: IMAGE_TO_REPLACE
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: crohns-database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: crohns-redis-credentials
              key: url
        - name: A2A_SERVICE_URL
          value: "http://crohns-a2a-service:8001"
        - name: LOG_LEVEL
          value: "info"
        - name: ENVIRONMENT
          value: "development"
        - name: PORT
          value: "8000"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
      volumes:
      - name: config-volume
        configMap:
          name: crohns-api-gateway-config

---
apiVersion: v1
kind: Service
metadata:
  name: crohns-api-gateway
  namespace: crohns
  labels:
    app: crohns-api-gateway
spec:
  selector:
    app: crohns-api-gateway
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: crohns-api-gateway-ingress
  namespace: crohns
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - dev.api.crohns-treatment.example.com
    secretName: crohns-api-tls
  rules:
  - host: dev.api.crohns-treatment.example.com
    http:
      paths:
      - path: /api/v1(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: crohns-api-gateway
            port:
              number: 8000
```

### Horizontal Pod Autoscaler

Create a file at `kubernetes/dev/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: crohns-api-gateway-hpa
  namespace: crohns
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: crohns-api-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 20
        periodSeconds: 60
```

## Pipeline Security

### Secrets Management

Implement the following security measures for secret management:

1. **GitHub Secrets**
   - Store sensitive credentials as GitHub repository secrets
   - Access secrets in workflows using `${{ secrets.SECRET_NAME }}`

2. **AWS Secrets Manager**
   - Store environment-specific secrets in AWS Secrets Manager
   - Retrieve secrets during deployment using IAM roles

3. **Kubernetes Secrets**
   - Store application secrets in Kubernetes secrets
   - Mount secrets as environment variables or files

### Example: Creating Kubernetes Secrets

Create a file at `kubernetes/scripts/create_secrets.sh`:

```bash
#!/bin/bash

# Create namespace if it doesn't exist
kubectl create namespace crohns --dry-run=client -o yaml | kubectl apply -f -

# Create database credentials secret
kubectl create secret generic crohns-database-credentials \
  --namespace=crohns \
  --from-literal=url="postgresql://user:password@postgres-host:5432/crohns_treatment" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Redis credentials secret
kubectl create secret generic crohns-redis-credentials \
  --namespace=crohns \
  --from-literal=url="redis://redis-host:6379/0" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create JWT secret
kubectl create secret generic crohns-jwt-secret \
  --namespace=crohns \
  --from-literal=jwt-secret="$(openssl rand -base64 32)" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create API credentials
kubectl create secret generic crohns-api-credentials \
  --namespace=crohns \
  --from-literal=api-key="$(openssl rand -base64 24)" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets created successfully."
```

## Integration with Third-Party Services

### Codecov Integration

1. Create a file at `.github/codecov.yml`:

```yaml
codecov:
  require_ci_to_pass: yes

coverage:
  precision: 2
  round: down
  range: "70...100"
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 80%
        threshold: 1%

parsers:
  gcov:
    branch_detection:
      conditional: yes
      loop: yes
      method: no
      macro: no

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: no
```

2. Add Codecov integration to your test workflow:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

### Sentry Integration

1. Install the Sentry SDK:

```bash
pip install sentry-sdk
```

2. Initialize Sentry in the application:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@sentry.example.com/1",
    integrations=[FlaskIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=0.5
)
```

3. Add Sentry release tracking to the deployment workflow:

```yaml
- name: Create Sentry release
  uses: getsentry/action-release@v1
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
    SENTRY_PROJECT: crohns-treatment-system
  with:
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
    version: ${{ github.sha }}
```

## Testing in the Pipeline

### Types of Tests

The pipeline includes several types of tests:

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete workflows
4. **Smoke Tests**: Basic tests to verify deployment success
5. **Performance Tests**: Test system performance under load

### Creating Test Fixtures

Create a file at `tests/conftest.py`:

```python
import os
import pytest
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_gateway.app import create_app
from src.data_layer.database import init_db, get_db


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file for SQLite database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the app with test config
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SERVER_NAME': 'localhost',
        'A2A_SERVICE_URL': 'http://localhost:8001',
        'GENETIC_ENGINE_URL': 'http://localhost:8002'
    })
    
    # Create the database and tables
    with app.app_context():
        init_db()
        
        # Insert test data
        db = get_db()
        # Add test data here
    
    yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def mock_genetic_engine(monkeypatch):
    """Fixture to mock the genetic engine responses."""
    
    class MockGeneticEngine:
        def optimize_treatment(self, patient_data):
            return {
                "treatment_plan": [
                    {
                        "medication": "Upadacitinib",
                        "dosage": "15",
                        "unit": "mg",
                        "frequency": "daily",
                        "duration": 90
                    }
                ],
                "fitness": 0.85
            }
    
    monkeypatch.setattr('src.coordination.genetic_engine_ffi.GeneticEngine', MockGeneticEngine)
    return MockGeneticEngine()
```

### Writing Smoke Tests

Create a file at `tests/smoke/test_dev_deployment.py`:

```python
import os
import requests
import time


def test_api_gateway_health():
    """Test the API Gateway health endpoint in the development environment."""
    base_url = os.getenv("API_GATEWAY_URL", "http://dev.api.crohns-treatment.example.com")
    
    # Retry logic for health checks
    max_retries = 5
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            
            # Check component health
            for component, status in health_data["components"].items():
                assert status["status"] in ["healthy", "degraded"]
            
            print("Health check passed")
            return
        except (requests.RequestException, AssertionError) as e:
            print(f"Attempt {i+1}/{max_retries} failed: {str(e)}")
            if i < max_retries - 1:
                time.sleep(retry_delay)
    
    # If we get here, all retries failed
    raise AssertionError("Health check failed after all retries")


def test_api_gateway_ready():
    """Test the API Gateway readiness endpoint in the development environment."""
    base_url = os.getenv("API_GATEWAY_URL", "http://dev.api.crohns-treatment.example.com")
    
    response = requests.get(f"{base_url}/ready", timeout=10)
    assert response.status_code == 200
    ready_data = response.json()
    assert ready_data["status"] == "ready"


def test_basic_api_functionality():
    """Test basic API functionality in the development environment."""
    base_url = os.getenv("API_GATEWAY_URL", "http://dev.api.crohns-treatment.example.com")
    
    # Test authentication
    auth_response = requests.post(
        f"{base_url}/api/v1/auth/token",
        json={"username": os.getenv("TEST_USERNAME"), "password": os.getenv("TEST_PASSWORD")},
        timeout=10
    )
    assert auth_response.status_code == 200
    token_data = auth_response.json()
    assert "access_token" in token_data
    
    # Use token for subsequent requests
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Test patient endpoint
    patients_response = requests.get(
        f"{base_url}/api/v1/patients",
        headers=headers,
        timeout=10
    )
    assert patients_response.status_code == 200
    
    # Test genetic engine integration
    optimize_response = requests.post(
        f"{base_url}/api/v1/treatment/optimize",
        headers=headers,
        json={"patient_id": "TEST001"},
        timeout=15
    )
    assert optimize_response.status_code in [200, 202]


if __name__ == "__main__":
    test_api_gateway_health()
    test_api_gateway_ready()
    test_basic_api_functionality()
    print("All smoke tests passed")
```

## Deployment Environments

### Environment Configuration

Create environment-specific configuration directories:

1. **Development Environment**:
   - Location: `kubernetes/dev/`
   - Purpose: Daily development and testing
   - Resource limits: Lower (to save costs)

2. **Staging Environment**:
   - Location: `kubernetes/staging/`
   - Purpose: Pre-production validation
   - Resource configuration: Mirror of production

3. **Production Environment**:
   - Location: `kubernetes/production/`
   - Purpose: Live system
   - Resource configuration: Optimized for performance and reliability

### Environment Configuration Management

Create a file at `config/environments/dev.json`:

```json
{
  "logging": {
    "level": "debug",
    "format": "json",
    "destination": "stdout"
  },
  "database": {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30
  },
  "api": {
    "rate_limit": 100,
    "timeout": 30
  },
  "genetic_engine": {
    "population_size": 50,
    "generations": 20,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8,
    "tournament_size": 3
  },
  "features": {
    "enable_self_healing": true,
    "enable_adaptive_trials": true,
    "enable_visualization": true,
    "enable_mock_services": true
  }
}
```

Create a file at `config/environments/production.json`:

```json
{
  "logging": {
    "level": "info",
    "format": "json",
    "destination": "file:/var/log/crohns-treatment-system.log"
  },
  "database": {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 60
  },
  "api": {
    "rate_limit": 1000,
    "timeout": 60
  },
  "genetic_engine": {
    "population_size": 200,
    "generations": 50,
    "mutation_rate": 0.05,
    "crossover_rate": 0.9,
    "tournament_size": 5
  },
  "features": {
    "enable_self_healing": true,
    "enable_adaptive_trials": true,
    "enable_visualization": true,
    "enable_mock_services": false
  }
}
```

## Monitoring and Observability

### Prometheus Configuration

Create a file at `infrastructure/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    scrape_interval: 5s
    static_configs:
      - targets: ['api-gateway:8000']

  - job_name: 'a2a-service'
    scrape_interval: 5s
    static_configs:
      - targets: ['a2a-service:8001']

  - job_name: 'genetic-engine'
    scrape_interval: 5s
    static_configs:
      - targets: ['genetic-engine:8002']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

### Grafana Dashboard

Create a file at `infrastructure/grafana/provisioning/dashboards/api-gateway.json`:

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "target": {
          "limit": 100,
          "matchAny": false,
          "tags": [],
          "type": "dashboard"
        },
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0.2,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "API Request Rate",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0.2,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "ms"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 3,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "API Response Time",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "orange",
                "value": 70
              },
              {
                "color": "red",
                "value": 85
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 8,
        "x": 0,
        "y": 9
      },
      "id": 4,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "mean"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "9.5.2",
      "title": "CPU Usage",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "orange",
                "value": 70
              },
              {
                "color": "red",
                "value": 85
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 8,
        "x": 8,
        "y": 9
      },
      "id": 5,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "mean"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "9.5.2",
      "title": "Memory Usage",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "orange",
                "value": 50
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 8,
        "x": 16,
        "y": 9
      },
      "id": 6,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "mean"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "9.5.2",
      "title": "Error Rate",
      "type": "gauge"
    }
  ],
  "refresh": "",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "API Gateway Dashboard",
  "version": 1,
  "weekStart": ""
}
```

## Pipeline Troubleshooting

### Common Issues and Solutions

#### Issue 1: Pipeline Build Failures

**Problem**: Builds fail intermittently in CI/CD pipeline.

**Solutions**:
1. Check for flaky tests and fix or mark as flaky
2. Increase timeouts for resource-intensive tests
3. Use caching for dependencies to speed up builds
4. Check for resource constraints in build agents

#### Issue 2: Deployment Failures

**Problem**: Kubernetes deployments fail during rollout.

**Solutions**:
1. Check image pull issues (credentials, image tag)
2. Verify resource requirements are appropriate
3. Check for configuration issues in deployment YAML
4. Use readiness probes to ensure smooth rollouts

#### Issue 3: Environment Configuration Mismatch

**Problem**: Code works in one environment but fails in another.

**Solutions**:
1. Use environment-specific configuration files
2. Set up database migrations properly
3. Ensure secrets and environment variables are correctly set
4. Use feature flags for environment-specific functionality

### Debugging Steps

1. **Check Pipeline Logs**:
   ```bash
   # View GitHub Actions logs via UI or API
   gh run view --job=JOB_ID
   ```

2. **Check Container Logs**:
   ```bash
   # View logs for a specific pod
   kubectl logs -n crohns -l app=crohns-api-gateway
   ```

3. **Check Deployment Status**:
   ```bash
   # Check deployment status
   kubectl describe deployment -n crohns crohns-api-gateway
   ```

4. **Exec into Containers**:
   ```bash
   # Get a shell in a pod for debugging
   kubectl exec -it -n crohns $(kubectl get pod -n crohns -l app=crohns-api-gateway -o jsonpath="{.items[0].metadata.name}") -- /bin/bash
   ```

## Conclusion

This CI/CD implementation provides a robust pipeline for building, testing, and deploying the Crohn's Treatment System. By following these configurations and best practices, the system can be reliably deployed across multiple environments with proper security, monitoring, and scalability.

Always remember to:
1. Keep your CI/CD configuration in version control
2. Regularly review and update dependencies
3. Monitor build and deployment times
4. Test your pipeline on a regular basis
5. Use infrastructure as code (IaC) for environment configuration

By following this guide, you'll have a production-ready CI/CD pipeline that ensures consistent and reliable deployments of the Crohn's Treatment System.