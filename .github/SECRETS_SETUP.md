# GitHub Secrets Setup Guide

## Quick Setup Commands

### 1. Get your Fly.io API token
```bash
fly auth token
```
Copy the output and add it as `FLY_API_TOKEN` in GitHub secrets.

### 2. Add secrets to GitHub

Go to: `https://github.com/chrisjowen/signallayer-monorepo/settings/secrets/actions`

Add these secrets:

| Secret Name | Description | How to get it |
|------------|-------------|---------------|
| `FLY_API_TOKEN` | Fly.io deployment token | Run `fly auth token` |
| `OPENAI_API_KEY` | OpenAI API key | Get from https://platform.openai.com/api-keys |
| `CODECOV_TOKEN` | (Optional) Coverage reporting | Get from https://codecov.io |

### 3. Set Fly.io secrets for signallayer-workflows

```bash
# Set all secrets at once
fly secrets set \
  OPENAI_API_KEY="your-openai-key" \
  GITHUB_TOKEN="your-github-token" \
  SCRAPING_BEE_API_KEY="your-scrapingbee-key" \
  WEB_TEMPORAL_URL="your-temporal-cloud-url:7233" \
  WORKER_TEMPORAL_URL="your-temporal-cloud-url:7233" \
  --app signallayer-workflows
```

### 4. Verify secrets

```bash
# GitHub secrets - check in the UI
# https://github.com/chrisjowen/signallayer-monorepo/settings/secrets/actions

# Fly.io secrets
fly secrets list --app signallayer-workflows
```

## First Deployment Checklist

### Workflows (signallayer-workflows)
- [ ] GitHub secrets configured (`FLY_API_TOKEN`, `OPENAI_API_KEY`)
- [ ] Fly.io app created (`fly apps create signallayer-workflows`)
- [ ] Fly.io secrets set (see command above)
- [ ] Temporal Cloud configured (or self-hosted Temporal)
- [ ] Code pushed to `main` branch
- [ ] GitHub Actions workflow runs successfully
- [ ] App scaled to desired size (`fly scale count web=2 worker=4 --process-groups --app signallayer-workflows`)

### UI (signallayer-ui)
- [ ] Choose deployment platform (Vercel, Netlify, Fly.io)
- [ ] Configure platform-specific secrets
- [ ] Update `.github/workflows/ci-cd.yml` with deployment steps

## Temporal Cloud Setup

SignalLayer uses Temporal for workflow orchestration. You have two options:

### Option 1: Temporal Cloud (Recommended for production)
1. Create account at https://cloud.temporal.io
2. Create a namespace
3. Generate API keys
4. Set the following secrets in Fly.io:
```bash
fly secrets set \
  WEB_TEMPORAL_URL="your-namespace.tmprl.cloud:7233" \
  WORKER_TEMPORAL_URL="your-namespace.tmprl.cloud:7233" \
  WEB_TEMPORAL_NAMESPACE="your-namespace" \
  WORKER_TEMPORAL_NAMESPACE="your-namespace" \
  TEMPORAL_API_KEY="your-api-key" \
  --app signallayer-workflows
```

### Option 2: Self-hosted Temporal
Deploy Temporal on Fly.io or another platform and configure accordingly.

## Testing the CI/CD Pipeline

1. **Create a test branch:**
   ```bash
   git checkout -b test/ci-cd
   ```

2. **Make a small change:**
   ```bash
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test CI/CD pipeline"
   ```

3. **Push and create PR:**
   ```bash
   git push origin test/ci-cd
   ```

4. **Check GitHub Actions:**
   - Go to `Actions` tab in GitHub
   - Verify PR checks run
   - Merge to `main` to trigger deployment

## Troubleshooting

### "FLY_API_TOKEN not found"
- Make sure you added the secret in GitHub repository settings
- Secret names are case-sensitive

### "Permission denied" during deployment
- Regenerate Fly.io token: `fly auth token`
- Update the `FLY_API_TOKEN` secret in GitHub

### Tests fail in CI
- Check if `OPENAI_API_KEY` is set in GitHub secrets
- Review test logs in GitHub Actions

### Temporal connection issues
- Verify Temporal URL and namespace are correct
- Check if Temporal Cloud credentials are set properly
- Ensure task queue name matches: `signallayer-queue`

### Deployment succeeds but app doesn't work
- Check Fly.io logs: `fly logs --app signallayer-workflows`
- Verify secrets are set: `fly secrets list --app signallayer-workflows`
