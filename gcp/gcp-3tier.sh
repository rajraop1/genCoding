#!/bin/bash

# Set variables
PROJECT_ID="marine-bebop-446518-j1"
REGION="us-central1"
CLUSTER_NAME="ecommerce-cluster"
DB_INSTANCE_NAME="ecommerce-db"
DB_USER="user"
DB_PASSWORD="password"
DB_NAME="ecommerce"
ARTIFACT_REPO="ecommerce-repo"

# Authenticate with GCP
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required services
gcloud services enable compute.googleapis.com container.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com

# Create an Artifact Registry repository
gcloud artifacts repositories create $ARTIFACT_REPO --repository-format=docker --location=$REGION

# Build and push Docker images
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/frontend ./frontend
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/backend ./backend

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/frontend
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/backend

# Create GKE Cluster
gcloud container clusters create $CLUSTER_NAME --num-nodes=2 --region=$REGION

# Get credentials for kubectl
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Deploy PostgreSQL using Cloud SQL
gcloud sql instances create $DB_INSTANCE_NAME --database-version=POSTGRES_13 --cpu=1 --memory=4GB --region=$REGION
gcloud sql users set-password $DB_USER --instance=$DB_INSTANCE_NAME --password=$DB_PASSWORD

# Get Cloud SQL Connection Name
DB_CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")

# Deploy Kubernetes resources
kubectl apply -f gcp_3tier_deployment.yaml

# Update backend deployment with Cloud SQL proxy
kubectl set env deployment/backend DATABASE_URL="postgres://$DB_USER:$DB_PASSWORD@127.0.0.1:5432/$DB_NAME"

echo "Deployment complete. Use 'kubectl get services' to check exposed endpoints."

