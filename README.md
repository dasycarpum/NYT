# NYT for New-York Times
## Data Engineer training project

The aim of this project is to use the NY Times developer portal, which offers several APIs to explore, to create its own API.

5 steps are planned :

* Data collection
* Data architecture
* Data consumption
* Putting data into production
* Workflow automation

# First app : Data collect

## Introduction

Use of the NY Times Books API to extract bestseller data in real time (once a week, on Mondays).  This data includes the url addresses of merchant sites such as Amazon and Apple Store, which will be scraped to provide additional data (no. of pages, stars, a hundred or so comments, genre, publication date, etc.). 
These data are cleaned and transformed by algorithms that will structure them for optimal use in 3 tables: Book, Review and Rank. All this will be stored in a relational database, PostgreSQL. A Dashboard for reporting

This app is an API that can be accessed locally via `http://0.0.0.0:80/`. This guide provides step-by-step instructions for deploying the application using Kubernetes.

---

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Git**: For cloning the repository. Download and install it from [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

2. **Docker**: The application runs in a Docker container. Install Docker by following instructions [here](https://docs.docker.com/get-docker/).

3. **Kubernetes**: This guide assumes you are familiar with Kubernetes and have it installed. If not, you can install it from [here](https://kubernetes.io/docs/setup/).

4. **kubectl**: This is the command-line tool for interacting with the Kubernetes cluster. Install it by following the instructions [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

---

## Installation Steps

### Step 1: Clone the Repository

Open a terminal and run the following command:

```bash
git clone https://github.com/dasycarpum/NYT.git
```

### Step 2: Navigate to the Project Directory

Change to the project directory by running:

```bash
cd NYT
```

### Step 3: Navigate to the 'k8s' Directory

Change to the 'k8s' directory where all the Kubernetes YAML configuration files are located:

```bash
cd k8s
```

### Step 4: Apply Kubernetes Configurations

Apply all Kubernetes configurations in the following order:

```bash
kubectl apply -f secret.yaml
kubectl apply -f dump.yaml
kubectl apply -f firefox.yaml
kubectl apply -f configmap.yaml
kubectl apply -f app_data.yaml
```

### Step 5: Confirm Deployment

Check if all the pods and services are running as expected:

```bash
kubectl get pods
kubectl get services
```

### Step 6: Access the API

At this point, your application should be running and, after 5-6 minutes, scraping time, the API can be accessed via `http://0.0.0.0:80/`.

---

## Troubleshooting

If you encounter any issues, you can check the logs for a specific pod using:

```bash
kubectl logs [Your-Pod-Name]
```

---

# Second app : Data query

## Introduction

An API for querying the database with configurable queries and returning results in JSON format files.

This app is an API that can be accessed locally via `http://0.0.0.0:80/endpoint`. This guide provides step-by-step instructions for deploying the application using Kubernetes.  Only steps 4 and 6 change, the others remain the same.

### Step 4: Apply Kubernetes Configurations

Apply all Kubernetes configurations in the following order:

```bash
kubectl apply -f secret.yaml
kubectl apply -f dump.yaml
kubectl apply -f app_api.yaml
```

### Step 6: Access the API

At this point, your application should be running, and the API can be accessed via 3 endpoints:

- `http://0.0.0.0:80/status`
- `http://0.0.0.0:80/all_genres`
- `http://0.0.0.0:80/best_book?year=2020&genre=Mysteries%20%26%20Thrillers`

---

# Third app : Machine Learning

## Introduction

This predictive model implements a Machine Learning algorithm and evaluates its effectiveness via specific metrics on a Dashboard.  
The aim is simple: to identify and understand the factual elements that contribute most to success in the bookshop, so as to better guide editorial and marketing decisions.

This app is an API that can be accessed locally via `http://0.0.0.0:80/`. This guide provides step-by-step instructions for deploying the application using Kubernetes.  Only steps 4 and 6 change, the others remain the same.

### Step 4: Apply Kubernetes Configurations

Apply all Kubernetes configurations in the following order:

```bash
kubectl apply -f secret.yaml
kubectl apply -f dump.yaml
kubectl apply -f app_ml.yaml
```

### Step 6: Access the API

At this point, your application should be running and the API can be accessed via `http://0.0.0.0:80/`.

---


