# How to develop with minikube

## 1. Create secret
Create secret by running `kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email>`. More information [here](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/).

## 2. Build image
Build the images you change with the `docker build -t gasparinorocha/wdm-<SERVICE>:<TAG> .` command. SERVICE can be order, payment or stock and TAG is an identifier. When testing, tag test or 0.0.0-SNAPSHOT. When pushing after testing, use semantic versioning (0.0.0).

## 3. Publish image
Push the image to docker hub with the `docker push gasparinorocha/wdm-<SERVICE>:<TAG>` command.

## 4. Change the tag in deployment files
To deploy the correct version, change the tag in the service's deployment file (e.g. `image: gasparinorocha/wdm-payment:0.0.1` -> `image: gasparinorocha/wdm-payment:0.0.2-SNAPSHOT`).

## 5. Redeploy pods in minikube
Run `kubectl apply -f .`. If on Windows (only on windows, I think), run minikube tunnel to access ingress-service (and then test stuff on localhost/{...}).