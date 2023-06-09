#!/usr/bin/env bash

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install -f helm-config/nginx-helm-values.yaml nginx ingress-nginx/ingress-nginx

sleep 7s

kubectl apply -f k8s/