#!/bin/bash

# Declare an array of deployments to delete
declare -a deployments=("postgres-db-deployment" "python-app")

# Declare an array of services to delete
declare -a services=("postgres-service" "python-app-service")

# Namespace in which to delete the resources
NAMESPACE="default"

# Loop to delete deployments
for deployment in "${deployments[@]}"
do
  echo "Deleting deployment ${deployment}..."
  kubectl delete deployment ${deployment} -n ${NAMESPACE}
done

# Loop to delete services
for service in "${services[@]}"
do
  echo "Deleting service ${service}..."
  kubectl delete service ${service} -n ${NAMESPACE}
done

kubectl delete ingress python-app-ingress -n ${NAMESPACE}

echo "All specified deployments and services have been deleted."
