# Monitoring stack (k3d demo)

This demo adds metrics collection and dashboards to the local k3d cluster.

## What was added
- Metrics Server for CPU/RAM metrics
- HPA based on CPU utilization
- Prometheus + Grafana (kube-prometheus-stack)
- Ingress for local routing

## Metrics Server (required for HPA and Lens)
```bash
kubectl apply --validate=false -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Verify:
```bash
kubectl get pods -n kube-system | grep metrics-server
kubectl top nodes
kubectl top pods
kubectl get hpa
```

## Prometheus + Grafana (kube-prometheus-stack)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

Check pods:
```bash
kubectl get pods -n monitoring
```

## Grafana access
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Open: `http://localhost:3000`

Get password:
```bash
kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

Suggested dashboards:
- Kubernetes / Compute Resources / Cluster
- Kubernetes / Compute Resources / Namespace (Pods)

## Notes
- HPA shows `cpu: <unknown>` until metrics-server is ready.
- Lens/OpenLens uses metrics-server for graphs.
