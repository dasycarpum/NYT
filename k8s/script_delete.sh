#!/bin/bash

# Declare an array of deployments to delete
declare -a deployments=("python-app" "firefox-deployment")

# Declare an array of statefulset to delete
declare -a statefulsets=("postgres-db")

# Declare an array of services to delete
declare -a services=("postgres-service" "python-app-service" "firefox-service")

# Namespace in which to delete the resources (accepts as a command-line argument)
NAMESPACE="$1"

# Validation to ensure NAMESPACE is not empty
if [ -z "$NAMESPACE" ]; then
  echo "Please provide a NAMESPACE as an argument."
  exit 1
fi

# Loop to delete deployments
for deployment in "${deployments[@]}"
do
  echo "Deleting deployment ${deployment}..."
  kubectl delete deployment ${deployment} -n ${NAMESPACE}
done

# Loop to delete statefulsets
for statefulset in "${statefulsets[@]}"
do
  echo "Deleting statefulset ${statefulset}..."
  kubectl delete statefulset ${statefulset} -n ${NAMESPACE}
done

# Loop to delete services
for service in "${services[@]}"
do
  echo "Deleting service ${service}..."
  kubectl delete service ${service} -n ${NAMESPACE}
done

kubectl delete ingress my-app-ingress -n ${NAMESPACE}

# kubectl delete pvc postgres-pvc -n ${NAMESPACE}

echo "All specified deployments and services have been deleted in NAMESPACE ${NAMESPACE}." 
