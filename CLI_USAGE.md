# Google Agent CLI (`agents-cli`) & Operations Guide

This document provides instructions for developing, evaluating, running, and deploying the **Smart Travel Concierge Agent** using the **Google Agent Development Kit (ADK) CLI** (`agents-cli`).

---

## 1. Prerequisites & Installation

Install `agents-cli` using `uv`:
```bash
uv tool install google-agents-cli
```

Verify installation:
```bash
agents-cli info
```

---

## 2. Running the Agent Locally

Start an interactive shell or programmatically execute the agent:

```bash
# Run agent interactively
agents-cli run travel_concierge

# Run ADK local API server with Pub/Sub & Eventarc triggers
agents-cli api_server --trigger_sources "pubsub,eventarc" travel_concierge
```

---

## 3. Evaluation & Regression Testing Suite

The repository includes a dedicated golden dataset regression evaluation suite under `tests/eval/`.

```bash
# 1. Run inference on golden dataset
agents-cli eval generate --dataset tests/eval/datasets/golden_dataset.json

# 2. Grade traces against evaluation metrics
agents-cli eval grade --config tests/eval/eval_config.yaml

# 3. Compare baseline vs new eval results
agents-cli eval compare artifacts/grade_results/baseline.json artifacts/grade_results/results_latest.json
```

Automated Pytest regression suite:
```bash
pytest tests/eval
```

---

## 4. Secure Secret Management (GCP Secret Manager)

Secrets such as `GEMINI_API_KEY` are retrieved securely via **Google Cloud Secret Manager** through [travel_concierge/secrets.py](file:///usr/local/google/home/yashashiremath/ai-in-5-days/travel_concierge/secrets.py):

```bash
# Create secret in GCP Secret Manager
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"

# Add secret version
echo -n "your-api-key" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
```

---

## 5. Infrastructure as Code & Cloud Run Deployment

Deploy infrastructure using Terraform (`infra/`):

```bash
cd infra
terraform init
terraform plan
terraform apply
```

Or deploy directly via `agents-cli`:
```bash
agents-cli deploy cloudrun --project your-gcp-project-id --region us-central1
```
