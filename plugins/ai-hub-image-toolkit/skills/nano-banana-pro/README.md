# Nano Banana Pro - Gemini Image Generation

Generate custom images using Gemini 3 Pro Image model for integration into frontend designs.

## Prerequisites

Authentication is handled via gcloud and PayPal's AI Platform Helper — no API key required.

### 1. Install and authenticate gcloud

```bash
# Install gcloud CLI: https://cloud.google.com/sdk/docs/install
gcloud auth application-default login
```

### 2. Set your team's GCP project

```bash
export GCP_PROJECT_NAME="your-gcp-project-name"
```

Add this to your shell profile (`~/.zshrc` or `~/.bashrc`) for persistence.

Ask your team lead for the correct project name (e.g., `us-ce1-test-apps-smbfs-engops`).
