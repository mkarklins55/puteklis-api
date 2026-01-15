# Kubernetes mini-demo (k3d or kind)

## Build container image

```bash
docker build -t puteklis-api:dev .
```

## Option A: k3d

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
k3d cluster create puteklis --api-port 6550 -p "8080:80@loadbalancer"
k3d image import puteklis-api:dev -c puteklis
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

Then open: `http://localhost:8080/api/health/`

## Option B: kind

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind create cluster
kind load docker-image puteklis-api:dev
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl port-forward svc/puteklis-api 8080:80
```

Then open: `http://localhost:8080/api/health/`
