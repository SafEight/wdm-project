#!/usr/bin/env bash

docker-compose build

# helm repo add bitnami https://charts.bitnami.com/bitnami
# helm repo update

# minikube start --insecure-registry="hostname:port"
# helm upgrade --install -f helm-config/redis-helm-values.yaml redis bitnami/redis

# docker run -d --name antidote1 -p "8087:8087" -e "NODE_NAME=antidote@antidote1" antidotedb/antidote:stable
minikube image load order:latest
minikube image load stock:latest
minikube image load user:latest

kubectl apply -f k8s-local/antidotedb.yaml
sleep 10
kubectl apply -f k8s-local/