# Where to Add XAI_API_KEY

## GitHub Repository Secrets

The XAI_API_KEY needs to be added as a **repository secret** in GitHub:

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
   - **Name:** `XAI_API_KEY`
   - **Value:** Your actual xAI API key (starts with `xai-...`)
   - Click "Add secret"

## Verify It's Added

After adding the secret, you should see it listed under:
```
Settings → Secrets and variables → Actions → Repository secrets
```

It will show as:
```
XAI_API_KEY    Updated X minutes ago
```

## How It Will Be Used

Once added, the secret will be accessible in:

### 1. GitHub Actions Workflows
The workflow file `.github/workflows/test_harness_e2e.yml` will access it via:
```yaml
env:
  XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
```

### 2. Run the Workflow

After committing the workflow file, you can:

**Option A: Automatic trigger**
- Push to the branch `copilot/replace-opencode-with-xai-api`
- The workflow will run automatically

**Option B: Manual trigger**
- Go to: `Actions` tab → `Harness End-to-End Test` workflow
- Click "Run workflow"
- Select branch: `copilot/replace-opencode-with-xai-api`
- Click "Run workflow"

### 3. For Local Testing

If you want to test locally (not in GitHub Actions):

Create a `.env` file in the repo root (NOT committed to git):
```bash
XAI_API_KEY=your_actual_xai_key_here
AGENT_MODEL=xai/grok-4-1-fast
USE_HARNESS=1
```

Then run:
```bash
./tests/test_harness_e2e.sh
```

## Current Situation

The Copilot agent environment cannot access repository secrets directly. The secret needs to be accessed through:

1. **GitHub Actions workflow** (recommended) - I've created the workflow file
2. **Local .env file** (for manual testing)

## Summary

**To complete the end-to-end test:**

1. ✅ Add `XAI_API_KEY` to repository secrets (Settings → Secrets and variables → Actions)
2. ✅ Commit the workflow file (`.github/workflows/test_harness_e2e.yml`)
3. ✅ Run the workflow from GitHub Actions tab
4. ✅ Check the results in the workflow run logs

The workflow will automatically run the test with your API key and show the results.
