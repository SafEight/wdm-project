# Web-scale Data Management Project - Group 20

## Deployment types:

### **Kubernetes cluster**

Run the `deploy-cloud.sh` script. If you get the following error `error when creating "k8s/ingress-service.yaml"`, run `kubectl apply -f k8s/`. To delete, run the `delete-cloud.sh` script.

***Requirements:*** You need to have access to kubectl of a k8s cluster.

### **Minikube** (local k8s cluster)

Run `deploy-charts-minikube-local.sh`.

***Requirements:*** You need to have minikube (with ingress enabled) and helm installed on your machine.

### **Docker-compose** (local development)

Run `docker-compose up --build`.

***Requirements:*** You need to have docker and docker-compose installed on your machine.

## Project structure

* `env`
    Folder containing the Redis env variables for the docker-compose deployment
    
* `helm-config` 
   Helm chart values for Redis and ingress-nginx
        
* `k8s`
    Folder containing the kubernetes deployments, apps and services for the ingress, order, payment and stock services.

* `k8s-local`
    Folder containing the kubernetes deployments, except they don't pull from the cloud

* `order`
    Folder containing the order application logic and dockerfile. 
    
* `payment`
    Folder containing the payment application logic and dockerfile. 

* `stock`
    Folder containing the stock application logic and dockerfile. 

* `test`
    Folder containing some basic correctness tests for the entire system. (Feel free to enhance them)
    
## Extra:
After implementing our synchronous SAGA based architecture we tried implementing a partly asynchronous Event-Driven architecture with a message queue. This was however not entirely consisten but did seem to scale very well. In the _7-implement-event-driven-architecture_ branch, you can run docker-compose up --build and see a working version with 6 (per microservice) proxies and 10 services (per microservice) running together. We did however not manage to deploy it with k8s (yet)
   
## Declaration of Honour:
- **Joey**: Stock implementation + start of proxies for event-driven architecture
- **Gaspar**: Sagas implementation + Cloud deployment/testing :( --> GCP's quotas inhibit horizontal scaling
- **Safouane**: Payment implementation + CRDT Investigation with antidoteDB :( --> Practical implementation of CRDT's with lowerbounds is lacking
- **Merlijn**: Order Implementation + Event Driven Architecture investigation :( --> Async programming is hard, k8s deployment was hard
