# Setup Guide: Cloud Run CI/CD & API Gateway

This guide details how to configure Google Cloud and GitHub for automated deployments of `aibot24-chat`.

## 1. Prerequisites (Google Cloud)
Ensure the following APIs are enabled in your project `aibot24-485301`:
- Cloud Run API
- Artifact Registry API
- IAM Credentials API
- API Gateway API
- Service Control API
- Service Management API

```bash
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    iamcredentials.googleapis.com \
    apigateway.googleapis.com \
    servicecontrol.googleapis.com \
    servicemanagement.googleapis.com
```

## 2. Infrastructure Setup

### Artifact Registry
Create a repository to store Docker images:
```bash
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Cloud Run"
```

### Service Account
Create a service account for GitHub Actions:
```bash
gcloud iam service-accounts create github-actions-deploy \
    --display-name="GitHub Actions Deployer"
```

Grant necessary roles:
```bash
SA_EMAIL="github-actions-deploy@aibot24-485301.iam.gserviceaccount.com"

# Allow pushing to Artifact Registry
gcloud projects add-iam-policy-binding aibot24-485301 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

# Allow deploying to Cloud Run
gcloud projects add-iam-policy-binding aibot24-485301 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

# Allow acting as service account (needed for Cloud Run runtime identity)
gcloud projects add-iam-policy-binding aibot24-485301 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"
```

## 3. Workload Identity Federation (WIF)
This allows GitHub Actions to authenticate without long-lived JSON keys.

1.  **Create Pool**:
    ```bash
    gcloud iam workload-identity-pools create "github-pool" \
      --project="aibot24-485301" \
      --location="global" \
      --display-name="GitHub Pool"
    ```

2.  **Create Provider**:
    ```bash
    gcloud iam workload-identity-pools providers create-oidc "github-provider" \
      --project="aibot24-485301" \
      --location="global" \
      --workload-identity-pool="github-pool" \
      --display-name="GitHub Provider" \
      --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
      --issuer-uri="https://token.actions.githubusercontent.com"
    ```

3.  **Allow GitHub Repo to Impersonate SA**:
    Replace `fordez/platform-agent-voice-text-bitrix24` with your actual `username/repo`.
    ```bash
    gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
      --project="aibot24-485301" \
      --role="roles/iam.workloadIdentityUser" \
      --member="principalSet://iam.googleapis.com/projects/485301/locations/global/workloadIdentityPools/github-pool/attribute.repository/fordez/platform-agent-voice-text-bitrix24"
    ```

4.  **Get WIF Provider String**:
    ```bash
    gcloud iam workload-identity-pools providers describe "github-provider" \
      --project="aibot24-485301" \
      --location="global" \
      --workload-identity-pool="github-pool" \
      --format="value(name)"
    ```
    *Copy this value. It looks like: `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider`*

## 4. GitHub Secrets
Go to your **GitHub Repository** -> **Settings** -> **Secrets and variables** -> **Actions**.

Add the following **Repository secrets**:

### Infrastructure Secrets
- `WF_PROVIDER`: (The full provider string from step 3.4, e.g., `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider`)
- `SERVICE_ACCOUNT`: `github-actions-deploy@aibot24-485301.iam.gserviceaccount.com`

### Application Environment Secrets (from your local .env)
Copy these global configuration values:
- `BOT_CODE`
- `BOT_NAME`
- `AGENT_VERSION`
- `WEBHOOK_HANDLER_URL`
- `LLM_PROVIDER`
- `AI_MODEL`
- `AI_TEMPERATURE`
- `AI_MAX_TOKENS`
- `FIRESTORE_PROJECT_ID`

> **Note**: Tenant-specific variables (like `CLIENT_ID`, `REFRESH_TOKEN`, `BITRIX_DOMAIN`) and **LLM API Keys** (`OPENAI_API_KEY`) are **NOT** needed here. 
> 
> The application fetches:
> 1.  **Bitrix Credentials**: From `config-secrets` (based on domain).
> 2.  **LLM API Keys**: From `config-ai` (based on tenant), cached in Redis.
> 
> **Agent Configuration**: The bot's personality (`role`, `objective`, `tone`, `knowledge`) is fetched dynamically from the **`agents`** collection in Firestore based on the active agent for the tenant. The `AI_*` variables above serve as **system-wide defaults** only.

## 5. API Gateway Setup
Once your Cloud Run service is deployed and you have its URL:

1.  Update `openapi2-run.yaml` with the backend address:
    ```yaml
    x-google-backend:
      address: https://aibot24-chat-xxxxx-uc.a.run.app
    ```

2.  Create the API Config:
    ```bash
    gcloud api-gateway api-configs create aibot24-chat-config-v1 \
      --api=aibot24-chat-api --openapi-spec=openapi2-run.yaml \
      --project=aibot24-485301 --backend-auth-service-account="${SA_EMAIL}"
    ```

3.  Create the Gateway:
    ```bash
    gcloud api-gateway gateways create aibot24-gateway \
      --api=aibot24-chat-api --api-config=aibot24-chat-config-v1 \
      --location=us-central1 --project=aibot24-485301
    ```
