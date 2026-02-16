# EXACTLY Where to Add XAI_API_KEY - No Confusion

## The ONLY Place You Need to Add It

### Repository Secrets (This is the one!)

**Step-by-step with exact clicks:**

1. **Go to your repository:**
   ```
   https://github.com/zfifteen/flaming-horse
   ```

2. **Click the "Settings" tab** (top of the page, next to "Insights")

3. **In the LEFT sidebar, look for "Security" section**

4. **Under "Security", click "Secrets and variables"**
   - This will expand to show sub-options

5. **Click "Actions"** (under "Secrets and variables")

6. **You'll see a green button "New repository secret"** - click it

7. **In the form:**
   - **Name:** `XAI_API_KEY` (exactly this, all caps)
   - **Secret:** Paste your xAI API key (the actual key value)
   - Click green "Add secret" button

8. **Done!** You should see it listed with a green checkmark

## Visual Path

```
GitHub Repo Page
  └─ Settings (tab at top)
      └─ Secrets and variables (left sidebar, under "Security")
          └─ Actions (click this)
              └─ Green "New repository secret" button
                  └─ Name: XAI_API_KEY
                  └─ Secret: your_key_here
                  └─ Click "Add secret"
```

## Why NOT the Other Places

### ❌ NOT "Codespaces secrets"
- This is for GitHub Codespaces only
- Won't work for GitHub Actions

### ❌ NOT "Dependabot secrets"  
- This is only for Dependabot
- Won't work for our workflow

### ❌ NOT Environment secrets
- These require environment setup
- Adds unnecessary complexity

### ❌ NOT Organization secrets
- Requires organization admin access
- Not needed for single repo

## Verify It's in the Right Place

After adding, you should see:

**Location:** Settings → Secrets and variables → Actions → Repository secrets

**List shows:**
```
Repository secrets
XAI_API_KEY        Updated X seconds ago        🗑️ (delete icon)
```

## Test It Works

Once added, the workflow will automatically pick it up. You can test by:

1. **Push this branch** (which triggers the workflow)
   
   OR

2. **Manually run the workflow:**
   - Go to **Actions** tab (top of repo)
   - Click **"Harness End-to-End Test"** (left sidebar)
   - Click **"Run workflow"** (blue button on right)
   - Select branch: `copilot/replace-opencode-with-xai-api`
   - Click **"Run workflow"** (green button)

The workflow will use `${{ secrets.XAI_API_KEY }}` which reads from Repository secrets.

## If You're Still Stuck

The exact URL for repository secrets is:
```
https://github.com/zfifteen/flaming-horse/settings/secrets/actions
```

Just replace `zfifteen` with your GitHub username if it's forked.

## Summary

**ONE place only:**
- Settings → Secrets and variables → Actions → New repository secret
- Name: `XAI_API_KEY`
- That's it!
