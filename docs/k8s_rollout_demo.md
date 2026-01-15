# K8s rollout + rollback demo

This short demo shows how Kubernetes updates a deployment and how to roll back.

## 1) Build a new image tag
```bash
docker build -t puteklis-api:dev2 .
k3d image import puteklis-api:dev2 -c puteklis
```

## 2) Rollout to the new image
```bash
kubectl set image deployment/puteklis-api app=puteklis-api:dev2
kubectl rollout status deployment/puteklis-api
```

Verify:
```bash
kubectl describe pod -l app=puteklis-api | grep Image:
```

## 3) Roll back to previous image
```bash
kubectl rollout undo deployment/puteklis-api
kubectl rollout status deployment/puteklis-api
```

Verify again:
```bash
kubectl describe pod -l app=puteklis-api | grep Image:
```
