#!/usr/bin/env bash

docker-compose build

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# minikube start
helm upgrade --install -f helm-config/redis-helm-values.yaml redis bitnami/redis
# for i in {7000..7007}; do
#     redis-server helm-config/$i/redis.conf --daemonize yes
# done

minikube image load order:latest
minikube image load stock:latest
minikube image load user:latest

kubectl apply -f k8s-local/