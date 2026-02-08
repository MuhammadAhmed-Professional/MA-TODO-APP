# Cloud Deployment Guide - Phase V

This guide explains how to deploy the Evolution of Todo app to a cloud Kubernetes cluster.

## Recommended Cloud Providers

| Provider | Free Tier | Pros | Setup Time |
|----------|-----------|------|------------|
| **Oracle OKE** | 4 OCPUs, 24GB RAM (Always Free) | No credit card, always free | 15 minutes |
| Google GKE | $300 credit (90 days) | Industry standard | 20 minutes |
| Azure AKS | $200 credit (30 days) | Enterprise features | 20 minutes |
| DigitalOcean | $200 credit (60 days) | Simple, fast | 10 minutes |

**Recommendation: Oracle OKE** for the hackathon - it's always free and requires no credit card.

---

## Option 1: Oracle Cloud Infrastructure (OCI) - Always Free ✅

### Step 1: Create Oracle Cloud Account

1. Go to: https://www.oracle.com/cloud/free/
2. Click "Sign Up" (you may need to use an existing email or create a new Oracle account)
3. Verify your email address
4. No credit card required!

### Step 2: Create OKE Cluster

1. Log in to Oracle Cloud Console
2. Navigate to **Developer Services** > **Kubernetes Clusters (OKE)**
3. Click **Create Cluster**
4. Select **Quick Create**
5. Configure:
   - **Name**: `todo-cluster`
   - **Compartment**: Select your compartment
   - **Kubernetes Version**: Latest (v1.29+)
   - **Shape**: `VM.Standard.E4.Flex` (Always Free eligible)
   - **Number of Nodes**: 1
   - **Node Shape**: `VM.Standard.E4.Flex`
   - **OCPUs per node**: 2
   - **Memory**: 8 GB
   - **Kubernetes Version**: Latest
6. Click **Create Cluster**
7. Wait 5-10 minutes for cluster creation

### Step 3: Configure kubectl

```bash
# Install OCI CLI (if not installed)
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash

# Configure OCI CLI
oci setup config

# Get cluster credentials
oci ce cluster create-kubeconfig --cluster-id <YOUR_CLUSTER_ID> --file $HOME/.kube/config --region us-ashburn-1

# Verify connection
kubectl get nodes
```

### Step 4: Set Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Add the following secrets:

| Secret Name | Value |
|-------------|-------|
| `CLOUD_PROVIDER` | `oracle` |
| `PROD_KUBECONFIG` | Base64 of your `~/.kube/config` file |

```bash
# To get base64 of kubeconfig
cat ~/.kube/config | base64 -w 0
```

### Step 5: Deploy

```bash
# Option A: Deploy via GitHub Actions (Recommended)
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# Then go to Actions tab and run "Production Deployment"

# Option B: Deploy manually via kubectl
kubectl apply -f phase-5/k8s/cloud/namespace.yaml
kubectl apply -f phase-5/dapr/components/
kubectl apply -f phase-5/k8s/cloud/
```

---

## Option 2: Google Cloud GKE

### Step 1: Create GCP Account

1. Go to: https://cloud.google.com/free
2. Click **Get started for free**
3. You'll need a credit card, but you get $300 credit for 90 days

### Step 2: Create GKE Cluster

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create cluster
gcloud container clusters create todo-cluster \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --num-nodes=1 \
    --disk-size=20GB \
    --cluster-version=latest

# Get credentials
gcloud container clusters get-credentials todo-cluster --zone=us-central1-a
```

### Step 3: Set Up GitHub Secrets

| Secret Name | Value |
|-------------|-------|
| `CLOUD_PROVIDER` | `gcp` |
| `GCP_CREDENTIALS` | Your GCP service account key (base64) |
| `GKE_CLUSTER_NAME` | `todo-cluster` |
| `GKE_LOCATION` | `us-central1-a` |

---

## Option 3: Azure AKS

### Step 1: Create Azure Account

1. Go to: https://azure.microsoft.com/en-us/free/
2. Click **Create free account**
3. You get $200 credit for 30 days + 12 months of free services

### Step 2: Create AKS Cluster

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create cluster
az aks create \
    --resource-group todo-rg \
    --name todo-cluster \
    --node-count 1 \
    --node-vm-size Standard_B2s \
    --enable-managed-identity \
    --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-cluster
```

---

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Docker images are built and pushed to a registry
- [ ] Kubernetes secrets are configured:
  - `postgres-credentials` - Neon DB connection string
  - `jwt-secret` - Your JWT secret
- [ ] Ingress domain is configured (update `phase-5/k8s/cloud/ingress.yaml`)
- [ ] Dapr is installed on the cluster

### Install Dapr on Kubernetes

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash -s latest

# Initialize Dapr on your cluster
dapr init -k

# Verify
dapr status -k
```

---

## Post-Deployment Verification

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get services -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Check HPA
kubectl get hpa -n todo-app

# Port-forward to test locally (optional)
kubectl port-forward -n todo-app svc/todo-frontend 3000:80
```

---

## Accessing Your Application

Once deployed:

1. **Get Ingress IP**:
   ```bash
   kubectl get ingress -n todo-app
   ```

2. **Update your DNS** (optional):
   - Add an A record pointing to the ingress IP

3. **Access the app**:
   - Frontend: `http://<INGRESS_IP>/`
   - API: `http://<INGRESS_IP>/api/`

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n todo-app

# View logs
kubectl logs <pod-name> -n todo-app

# Dapr sidecar logs
kubectl logs <pod-name> -c dapr -n todo-app
```

### Image Pull Errors

Ensure images are public or your registry credentials are configured:

```bash
# Create registry secret
kubectl create secret docker-registry ghcr-login \
  --docker-server=ghcr.io \
  --docker-username=<your-username> \
  --docker-password=<your-token> \
  -n todo-app
```

### Kafka Not Ready

```bash
# Check Strimzi operator
kubectl get pods -n todo-app | grep strimzi

# Check Kafka cluster status
kubectl get kafka -n todo-app

# View Kafka logs
kubectl logs -n todo-app <kafka-pod>
```

---

## Cleanup

```bash
# Delete all resources
kubectl delete namespace todo-app

# Delete Dapr
dapr uninstall -k

# For Oracle: Delete cluster from console
# For GCP:
gcloud container clusters delete todo-cluster --zone=us-central1-a

# For Azure:
az aks delete --resource-group todo-rg --name todo-cluster
```

---

## Cost Estimate

| Provider | Monthly Cost (After Free Tier) |
|----------|-------------------------------|
| Oracle OKE | **$0** (Always Free) |
| GKE | ~$30/month (e2-medium, 1 node) |
| AKS | ~$25/month (B2s, 1 node) |
| DigitalOcean | ~$24/month (basic droplet, K8s) |

---

**Next Steps**:
1. Choose your cloud provider
2. Create cluster
3. Configure GitHub secrets
4. Deploy via GitHub Actions or kubectl
5. Verify deployment
6. Update ingress with your domain (optional)

Good luck! 🚀
