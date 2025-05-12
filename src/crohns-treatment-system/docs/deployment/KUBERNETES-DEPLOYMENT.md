# Kubernetes Deployment Guide

This document provides detailed instructions for deploying the Crohn's Treatment System on Kubernetes. It covers cluster setup, deployment manifests, resource optimization, and operational best practices.

## Table of Contents

1. [Kubernetes Architecture](#kubernetes-architecture)
2. [Prerequisites](#prerequisites)
3. [Cluster Setup](#cluster-setup)
4. [Namespace and RBAC](#namespace-and-rbac)
5. [Deployment Manifests](#deployment-manifests)
6. [StatefulSet Components](#statefulset-components)
7. [ConfigMaps and Secrets](#configmaps-and-secrets)
8. [Ingress Configuration](#ingress-configuration)
9. [Persistent Storage](#persistent-storage)
10. [Resource Management](#resource-management)
11. [Autoscaling](#autoscaling)
12. [Health Checks](#health-checks)
13. [Network Policies](#network-policies)
14. [Monitoring and Logging](#monitoring-and-logging)
15. [Maintenance and Updates](#maintenance-and-updates)
16. [Backup and Disaster Recovery](#backup-and-disaster-recovery)

## Kubernetes Architecture

The Kubernetes deployment for the Crohn's Treatment System follows a microservices architecture with the following components:

```
┌───────────────────────────────────────────────────────────────┐
│                       Kubernetes Cluster                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Ingress Controller                    │  │
│  └─────────────────────────────┬───────────────────────────┘  │
│                                │                              │
│  ┌────────────────┐  ┌─────────▼────────┐  ┌────────────────┐ │
│  │   API Gateway  │◄─┤  Service Mesh    ├─►│   Web UI       │ │
│  └────────┬───────┘  └─────────┬────────┘  └────────┬───────┘ │
│           │                    │                    │         │
│  ┌────────▼───────┐  ┌─────────▼────────┐  ┌────────▼───────┐ │
│  │  A2A Service   │  │ Adaptive Trial   │  │  Visualization │ │
│  └────────┬───────┘  │     Service      │  │    Service     │ │
│           │          └─────────┬────────┘  └────────────────┘ │
│  ┌────────▼───────┐            │                              │
│  │ Genetic Engine │            │                              │
│  └────────────────┘            │                              │
│                                │                              │
│  ┌────────────────┐  ┌─────────▼────────┐  ┌────────────────┐ │
│  │   PostgreSQL   │  │      Redis       │  │  ElasticSearch │ │
│  └────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Prerequisites

Before deploying the Crohn's Treatment System to Kubernetes, ensure you have:

1. **Kubernetes Cluster**: A running Kubernetes cluster (version 1.22+)
2. **kubectl**: The Kubernetes command-line tool configured to communicate with your cluster
3. **Helm**: Package manager for Kubernetes (version 3.8+)
4. **Container Registry**: Access to a container registry (e.g., ECR, Docker Hub)
5. **Storage Provisioner**: A storage provisioner for persistent volumes (e.g., EBS, PVC)
6. **Domain Name**: A domain name for ingress configuration
7. **SSL Certificates**: SSL certificates for secure communication

## Cluster Setup

### 1. Create an EKS Cluster (AWS Example)

```bash
# Create an EKS cluster with eksctl
eksctl create cluster \
  --name crohns-treatment-cluster \
  --version 1.24 \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type m5.large \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 6 \
  --managed
```

### 2. Add Node Groups for Specialized Workloads

```bash
# Add a node group for compute-intensive workloads (genetic engine)
eksctl create nodegroup \
  --cluster crohns-treatment-cluster \
  --region us-west-2 \
  --name compute-workers \
  --node-type c5.2xlarge \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --node-labels "workload=compute" \
  --node-taints "compute=true:NoSchedule"

# Add a node group for database workloads
eksctl create nodegroup \
  --cluster crohns-treatment-cluster \
  --region us-west-2 \
  --name database-workers \
  --node-type r5.xlarge \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --node-labels "workload=database" \
  --node-taints "database=true:NoSchedule"
```

### 3. Install Core Addons

```bash
# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=crohns-treatment-cluster \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller

# Install cert-manager for TLS certificates
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Install Prometheus and Grafana for monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

## Namespace and RBAC

### 1. Create Namespace

Create a dedicated namespace for the Crohn's Treatment System:

```yaml
# crohns-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: crohns
  labels:
    name: crohns
    environment: production
```

Apply the namespace:

```bash
kubectl apply -f crohns-namespace.yaml
```

### 2. Create Service Account

Create a service account for the application:

```yaml
# crohns-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: crohns-service-account
  namespace: crohns
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: crohns-role
  namespace: crohns
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: crohns-role-binding
  namespace: crohns
subjects:
- kind: ServiceAccount
  name: crohns-service-account
  namespace: crohns
roleRef:
  kind: Role
  name: crohns-role
  apiGroup: rbac.authorization.k8s.io
```

Apply the service account and RBAC configuration:

```bash
kubectl apply -f crohns-service-account.yaml
```

## Deployment Manifests

### 1. API Gateway Deployment

```yaml
# api-gateway-deployment.yaml
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
      serviceAccountName: crohns-service-account
      containers:
      - name: api-gateway
        image: ${REGISTRY}/crohns-api-gateway:${VERSION}
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
          value: "production"
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
```

### 2. A2A Service Deployment

```yaml
# a2a-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crohns-a2a-service
  namespace: crohns
  labels:
    app: crohns-a2a-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crohns-a2a-service
  template:
    metadata:
      labels:
        app: crohns-a2a-service
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: "/metrics"
        prometheus.io/port: "8001"
    spec:
      serviceAccountName: crohns-service-account
      containers:
      - name: a2a-service
        image: ${REGISTRY}/crohns-a2a-service:${VERSION}
        imagePullPolicy: Always
        ports:
        - containerPort: 8001
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
        - name: GENETIC_ENGINE_URL
          value: "http://crohns-genetic-engine:8002"
        - name: LOG_LEVEL
          value: "info"
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
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: crohns-a2a-service
  namespace: crohns
  labels:
    app: crohns-a2a-service
spec:
  selector:
    app: crohns-a2a-service
  ports:
  - port: 8001
    targetPort: 8001
    name: http
  type: ClusterIP
```

### 3. Genetic Engine Deployment

```yaml
# genetic-engine-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crohns-genetic-engine
  namespace: crohns
  labels:
    app: crohns-genetic-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crohns-genetic-engine
  template:
    metadata:
      labels:
        app: crohns-genetic-engine
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: "/metrics"
        prometheus.io/port: "8002"
    spec:
      serviceAccountName: crohns-service-account
      nodeSelector:
        workload: compute
      tolerations:
      - key: "compute"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: genetic-engine
        image: ${REGISTRY}/crohns-genetic-engine:${VERSION}
        imagePullPolicy: Always
        ports:
        - containerPort: 8002
          name: http
        env:
        - name: LOG_LEVEL
          value: "info"
        - name: POPULATION_SIZE
          value: "200"
        - name: GENERATIONS
          value: "50"
        - name: MUTATION_RATE
          value: "0.05"
        - name: CROSSOVER_RATE
          value: "0.9"
        resources:
          limits:
            cpu: "4"
            memory: "8Gi"
          requests:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8002
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: crohns-genetic-engine
  namespace: crohns
  labels:
    app: crohns-genetic-engine
spec:
  selector:
    app: crohns-genetic-engine
  ports:
  - port: 8002
    targetPort: 8002
    name: http
  type: ClusterIP
```

## StatefulSet Components

### 1. PostgreSQL StatefulSet

For production deployments, it's recommended to use a managed database service like Amazon RDS. However, for completeness, here's a StatefulSet for PostgreSQL:

```yaml
# postgresql-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: crohns-postgres
  namespace: crohns
spec:
  serviceName: crohns-postgres
  replicas: 1
  selector:
    matchLabels:
      app: crohns-postgres
  template:
    metadata:
      labels:
        app: crohns-postgres
    spec:
      nodeSelector:
        workload: database
      tolerations:
      - key: "database"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: crohns-database-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crohns-database-credentials
              key: password
        - name: POSTGRES_DB
          value: crohns_treatment
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: gp2
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: crohns-postgres
  namespace: crohns
spec:
  selector:
    app: crohns-postgres
  ports:
  - port: 5432
    targetPort: 5432
    name: postgres
  clusterIP: None
```

### 2. Redis StatefulSet

```yaml
# redis-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: crohns-redis
  namespace: crohns
spec:
  serviceName: crohns-redis
  replicas: 1
  selector:
    matchLabels:
      app: crohns-redis
  template:
    metadata:
      labels:
        app: crohns-redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--appendonly", "yes"]
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          limits:
            cpu: "500m"
            memory: "1Gi"
          requests:
            cpu: "200m"
            memory: "512Mi"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: gp2
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: crohns-redis
  namespace: crohns
spec:
  selector:
    app: crohns-redis
  ports:
  - port: 6379
    targetPort: 6379
    name: redis
  clusterIP: None
```

## ConfigMaps and Secrets

### 1. API Gateway ConfigMap

```yaml
# api-gateway-configmap.yaml
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
        "allowed_origins": ["https://crohns-treatment-portal.example.com"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allowed_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Length"],
        "max_age": 86400
      },
      "security": {
        "rate_limit": {
          "enabled": true,
          "requests_per_minute": 1000,
          "burst": 200
        },
        "authentication": {
          "enabled": true,
          "token_expiration_seconds": 3600
        }
      },
      "services": {
        "a2a_service": {
          "url": "http://crohns-a2a-service:8001",
          "timeout_seconds": 30,
          "retry": {
            "max_attempts": 3,
            "initial_backoff_ms": 100
          }
        }
      }
    }
```

### 2. Genetic Engine ConfigMap

```yaml
# genetic-engine-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: crohns-genetic-engine-config
  namespace: crohns
data:
  config.json: |
    {
      "genetic_algorithm": {
        "population_size": 200,
        "generations": 50,
        "mutation_rate": 0.05,
        "crossover_rate": 0.9,
        "tournament_size": 5,
        "elitism_percentage": 0.1
      },
      "fitness_function": {
        "efficacy_weight": 0.5,
        "safety_weight": 0.3,
        "cost_weight": 0.1,
        "adherence_weight": 0.1
      },
      "logging": {
        "level": "info",
        "format": "json"
      }
    }
```

### 3. Database Credentials Secret

Create the database credentials secret securely:

```bash
# Create a Kubernetes secret for database credentials
kubectl create secret generic crohns-database-credentials \
  --namespace=crohns \
  --from-literal=username=postgres \
  --from-literal=password=$(openssl rand -base64 24) \
  --from-literal=url="postgresql://postgres:$(openssl rand -base64 24)@crohns-postgres:5432/crohns_treatment"
```

### 4. Redis Credentials Secret

```bash
# Create a Kubernetes secret for Redis credentials
kubectl create secret generic crohns-redis-credentials \
  --namespace=crohns \
  --from-literal=url="redis://crohns-redis:6379/0"
```

### 5. JWT Secret

```bash
# Create a Kubernetes secret for JWT authentication
kubectl create secret generic crohns-jwt-secret \
  --namespace=crohns \
  --from-literal=secret=$(openssl rand -base64 32)
```

## Ingress Configuration

### 1. Ingress Resource

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: crohns-ingress
  namespace: crohns
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-XSS-Protection: 1; mode=block";
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
  - hosts:
    - api.crohns-treatment.example.com
    secretName: crohns-api-tls
  rules:
  - host: api.crohns-treatment.example.com
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

### 2. ClusterIssuer for TLS Certificates

```yaml
# cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: admin@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

## Persistent Storage

### 1. StorageClass Configuration

Using AWS EBS as an example:

```yaml
# storage-classes.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp2
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-io
provisioner: kubernetes.io/aws-ebs
parameters:
  type: io1
  iopsPerGB: "50"
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### 2. Backup PVC

```yaml
# backup-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: crohns-backup-pvc
  namespace: crohns
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp2
  resources:
    requests:
      storage: 100Gi
```

## Resource Management

### 1. Resource Quotas

```yaml
# resource-quotas.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: crohns-quota
  namespace: crohns
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "50"
    services: "30"
    persistentvolumeclaims: "20"
    secrets: "20"
    configmaps: "20"
```

### 2. Limit Ranges

```yaml
# limit-ranges.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: crohns-limits
  namespace: crohns
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 200m
      memory: 256Mi
    min:
      cpu: 50m
      memory: 64Mi
    max:
      cpu: 4
      memory: 8Gi
```

## Autoscaling

### 1. Horizontal Pod Autoscaler

```yaml
# api-gateway-hpa.yaml
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

### 2. Vertical Pod Autoscaler (Optional)

If using VPA:

```yaml
# api-gateway-vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: crohns-api-gateway-vpa
  namespace: crohns
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: crohns-api-gateway
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 200m
        memory: 256Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
```

## Health Checks

### 1. Liveness and Readiness Probes

Liveness and readiness probes are already included in the deployment manifests. Here's an explanation of the configuration:

- **Liveness Probe**: Determines if a container is running properly. If the probe fails, Kubernetes restarts the container.
- **Readiness Probe**: Determines if a container is ready to serve traffic. If the probe fails, Kubernetes stops sending traffic to the pod.

### 2. Pod Disruption Budget

```yaml
# api-gateway-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: crohns-api-gateway-pdb
  namespace: crohns
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: crohns-api-gateway
```

## Network Policies

```yaml
# network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-gateway-network-policy
  namespace: crohns
spec:
  podSelector:
    matchLabels:
      app: crohns-api-gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: default
    - podSelector:
        matchLabels:
          app: nginx-ingress-controller
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: crohns-a2a-service
    ports:
    - protocol: TCP
      port: 8001
  - to:
    - podSelector:
        matchLabels:
          app: crohns-postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: crohns-redis
    ports:
    - protocol: TCP
      port: 6379
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: a2a-service-network-policy
  namespace: crohns
spec:
  podSelector:
    matchLabels:
      app: crohns-a2a-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: crohns-api-gateway
    ports:
    - protocol: TCP
      port: 8001
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: crohns-genetic-engine
    ports:
    - protocol: TCP
      port: 8002
  - to:
    - podSelector:
        matchLabels:
          app: crohns-postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: crohns-redis
    ports:
    - protocol: TCP
      port: 6379
```

## Monitoring and Logging

### 1. ServiceMonitor for Prometheus

```yaml
# service-monitors.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: crohns-api-gateway-monitor
  namespace: crohns
  labels:
    app: crohns-api-gateway
    release: prometheus
spec:
  selector:
    matchLabels:
      app: crohns-api-gateway
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: crohns-a2a-service-monitor
  namespace: crohns
  labels:
    app: crohns-a2a-service
    release: prometheus
spec:
  selector:
    matchLabels:
      app: crohns-a2a-service
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: crohns-genetic-engine-monitor
  namespace: crohns
  labels:
    app: crohns-genetic-engine
    release: prometheus
spec:
  selector:
    matchLabels:
      app: crohns-genetic-engine
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
```

### 2. PrometheusRule for Alerts

```yaml
# prometheus-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: crohns-alerts
  namespace: crohns
  labels:
    release: prometheus
spec:
  groups:
  - name: crohns.rules
    rules:
    - alert: HighErrorRate
      expr: sum(rate(http_requests_total{status=~"5..",app=~"crohns-.*"}[5m])) / sum(rate(http_requests_total{app=~"crohns-.*"}[5m])) > 0.05
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is above 5% for 1 minute (current value: {{ $value }})"
    - alert: ServiceDown
      expr: up{app=~"crohns-.*"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Service down: {{ $labels.app }}"
        description: "{{ $labels.app }} has been down for more than 1 minute"
    - alert: HighCpuUsage
      expr: sum(rate(container_cpu_usage_seconds_total{container!="POD",namespace="crohns"}[1m])) / sum(container_spec_cpu_quota{container!="POD",namespace="crohns"} / 100000) > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage: {{ $labels.app }}"
        description: "{{ $labels.app }} has high CPU usage for more than 5 minutes (current value: {{ $value }})"
```

### 3. ConfigMap for FluentBit Logging

```yaml
# fluentbit-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentbit-config
  namespace: crohns
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        Parsers_File parsers.conf

    [INPUT]
        Name             tail
        Tag              kube.*
        Path             /var/log/containers/*crohns*.log
        Parser           docker
        DB               /var/log/fluentbit.db
        Mem_Buf_Limit    5MB
        Skip_Long_Lines  On
        Refresh_Interval 10

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Merge_Log           On
        K8S-Logging.Parser  On
        K8S-Logging.Exclude Off

    [OUTPUT]
        Name            es
        Match           *
        Host            ${FLUENT_ELASTICSEARCH_HOST}
        Port            ${FLUENT_ELASTICSEARCH_PORT}
        Logstash_Format On
        Logstash_Prefix crohns
        Replace_Dots    On
        Retry_Limit     False
        tls             On
        tls.verify      Off

  parsers.conf: |
    [PARSER]
        Name   json
        Format json
        Time_Key time
        Time_Format %d/%b/%Y:%H:%M:%S %z

    [PARSER]
        Name        docker
        Format      json
        Time_Key    time
        Time_Format %Y-%m-%dT%H:%M:%S.%L
        Time_Keep   On
```

## Maintenance and Updates

### 1. Update Strategy

For most deployments, we recommend using a RollingUpdate strategy as configured in the deployment manifests. This ensures zero-downtime updates.

### 2. Manual Database Migrations

Before upgrading applications, you may need to run database migrations:

```bash
# Create a job to run database migrations
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: crohns-db-migrate
  namespace: crohns
spec:
  ttlSecondsAfterFinished: 100
  template:
    spec:
      containers:
      - name: migrate
        image: ${REGISTRY}/crohns-api-gateway:${VERSION}
        command: ["python", "-m", "src.data_layer.database.migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: crohns-database-credentials
              key: url
      restartPolicy: Never
  backoffLimit: 4
EOF
```

### 3. Performing Backups

Set up a CronJob for regular database backups:

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: crohns-db-backup
  namespace: crohns
spec:
  schedule: "0 1 * * *"  # Run at 1 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h crohns-postgres -U "$POSTGRES_USER" -d crohns_treatment -F c -f /backup/crohns_treatment_$(date +%Y%m%d).dump
              aws s3 cp /backup/crohns_treatment_$(date +%Y%m%d).dump s3://crohns-treatment-backups/
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: crohns-database-credentials
                  key: username
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: crohns-database-credentials
                  key: password
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: crohns-backup-pvc
          restartPolicy: OnFailure
```

## Backup and Disaster Recovery

### 1. Backup Strategy

Implement a comprehensive backup strategy:

1. **Database Backups**: Daily snapshots using the CronJob above
2. **PVC Backups**: Snapshot PVCs regularly using Kubernetes snapshot APIs
3. **Configuration Backups**: Store all Kubernetes manifests in version control
4. **Offsite Storage**: Store backups in multiple regions/providers

### 2. Disaster Recovery Plan

Document a disaster recovery plan:

1. **RTO (Recovery Time Objective)**: How quickly you need to restore services
2. **RPO (Recovery Point Objective)**: Maximum acceptable data loss
3. **Recovery Steps**: Detailed steps to restore from backups
4. **Alternative Region Failover**: Instructions to deploy to a different region
5. **Regular Testing**: Schedule and procedure for testing the recovery plan

### 3. Multi-Region Deployment (Optional)

For critical deployments, consider a multi-region setup:

1. **Active-Passive**: Primary region handles all traffic, secondary region on standby
2. **Active-Active**: Traffic distributed across regions with global load balancing
3. **Database Replication**: Replicate data across regions
4. **Global DNS**: Route traffic using DNS-based health checks

## Conclusion

This deployment guide provides a comprehensive approach to deploying the Crohn's Treatment System on Kubernetes. By following these guidelines, you can ensure a scalable, reliable, and maintainable deployment that meets production requirements.

Remember to adjust the configuration based on your specific needs, especially resource requirements and scaling parameters. Regularly test your deployment and disaster recovery procedures to ensure they work as expected.

For any questions or issues, please contact the deployment team at deployment-team@example.com.