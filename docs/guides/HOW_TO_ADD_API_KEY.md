# Where to Add LLM API Keys

## Local Configuration (.env file)

For local development, add your API keys to the `.env` file in the repo root (NOT committed to git).

### Configuration

The harness uses provider-agnostic configuration. Set `LLM_PROVIDER` to switch between providers:

```bash
# LLM Provider Configuration
LLM_PROVIDER=XAI
# LLM_PROVIDER=MINIMAX

# Provider-Specific Keys
XAI_API_KEY=your_xai_key_here
MINIMAX_API_KEY=your_minimax_key_here

# Provider-Specific Base URLs (optional - defaults provided)
XAI_BASE_URL=https://api.x.ai/v1
MINIMAX_BASE_URL=https://api.minimax.io/v1

# Provider-Specific Models (optional - defaults provided)
XAI_MODEL=grok-code-fast-1
MINIMAX_MODEL=MiniMax-M2.5
```

### Switching Providers

To switch between providers, just change `LLM_PROVIDER`:

```bash
# Use XAI (default)
LLM_PROVIDER=XAI

# Use MiniMax
# LLM_PROVIDER=XAI
LLM_PROVIDER=MINIMAX
```

All provider keys can remain in the `.env` - only change `LLM_PROVIDER` to switch.

## GitHub Repository Secrets

For GitHub Actions, add keys as repository secrets:

### Steps:

1. **Go to your GitHub repository:**
   ```
   https://github.com/zfifteen/flaming-horse
   ```

2. **Click on "Settings"** (top menu bar)

3. **In the left sidebar, click:**
   - "Secrets and variables"
   - Then click "Actions"

4. **Click "New repository secret"**

5. **Add the secret:**
   - **Name:** `XAI_API_KEY` or `MINIMAX_API_KEY`
   - **Value:** Your actual API key
   - Click "Add secret"

## Verify It's Added

After adding the secret, you should see it listed under:
```
Settings → Secrets and variables → Actions → Repository secrets
```

## How It Will Be Used

Once added, the secret will be accessible in GitHub Actions workflows:

```yaml
env:
  XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
  MINIMAX_API_KEY: ${{ secrets.MINIMAX_API_KEY }}
```

## Summary

1. Add API keys to `.env` for local development
2. Add API keys to GitHub secrets for CI/CD
3. Set `LLM_PROVIDER` to switch between XAI and MINIMAX
