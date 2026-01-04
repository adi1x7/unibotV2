# GitHub Push Guide

This guide will help you push your UniBot code to GitHub while excluding sensitive files and large data.

## Files Excluded from Git

The following files/directories are automatically excluded via `.gitignore`:

- ✅ **ChromaDB embeddings** (`chroma_db/` and all subdirectories)
- ✅ **Virtual environment** (`venv/`)
- ✅ **Environment variables** (`.env`, `.env.local`)
- ✅ **Python cache** (`__pycache__/`, `*.pyc`)
- ✅ **Scrape tracking files** (`scrape_tracker.json`, `scrape_checkpoint.json`)
- ✅ **Database files** (`*.db`, `*.sqlite3`)
- ✅ **IDE files** (`.vscode/`, `.idea/`)

## Pre-Push Checklist

Before pushing to GitHub, verify:

1. ✅ `.env` file is not tracked (contains API keys)
2. ✅ `chroma_db/` directory is not tracked (large embeddings)
3. ✅ `venv/` directory is not tracked (virtual environment)
4. ✅ No sensitive data in code files

## Steps to Push to GitHub

### 1. Check What Will Be Committed

```bash
cd C:\Users\novap\Desktop\unibot_\unibot_
git status
```

Verify that `chroma_db/`, `venv/`, and `.env` are NOT in the list.

### 2. Stage Your Changes

```bash
git add .
```

Or stage specific files:
```bash
git add .gitignore
git add frontend/
git add *.py
git add README.md
# etc.
```

### 3. Commit Your Changes

```bash
git commit -m "Your commit message here"
```

Example:
```bash
git commit -m "Fix frontend-backend connection and improve LLM tool usage"
```

### 4. Push to GitHub

If this is your first push:
```bash
git remote add origin https://github.com/yourusername/unibot.git
git branch -M main
git push -u origin main
```

If you've already set up the remote:
```bash
git push
```

Or push to a specific branch:
```bash
git push origin main
```

## Verify Exclusions

After pushing, verify on GitHub that:
- ❌ No `chroma_db/` directory appears
- ❌ No `venv/` directory appears
- ❌ No `.env` file appears

## If Files Were Already Committed

If you accidentally committed sensitive files before, you need to remove them from Git history:

```bash
# Remove from Git (but keep locally)
git rm --cached .env
git rm -r --cached chroma_db/
git rm -r --cached venv/

# Commit the removal
git commit -m "Remove sensitive files from repository"

# Push the changes
git push
```

**Note:** If sensitive data was already pushed, you should:
1. Rotate/regenerate your API keys
2. Consider using GitHub's secret scanning feature
3. For complete removal, you may need to rewrite Git history (advanced)

## Setting Up a New Repository

If you're creating a new GitHub repository:

1. **Create repository on GitHub** (don't initialize with README)
2. **Add remote:**
   ```bash
   git remote add origin https://github.com/yourusername/unibot.git
   ```
3. **Push:**
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Recommended Repository Structure

Your repository should include:
- ✅ Source code (`.py` files)
- ✅ Frontend files (`frontend/*.html`, `frontend/*.js`, `frontend/*.css`)
- ✅ Configuration files (`requirements.txt`, `.gitignore`)
- ✅ Documentation (`README.md`, `STARTUP_FIXES.md`, etc.)
- ✅ Startup scripts (`start_frontend.bat`, `start_frontend.sh`)

Should NOT include:
- ❌ `.env` (create `.env.example` instead)
- ❌ `chroma_db/` (users will generate their own)
- ❌ `venv/` (users will create their own)
- ❌ `__pycache__/`
- ❌ Large data files

## Creating .env.example

Create a template file for users:

```bash
# Copy .env to .env.example (remove actual values)
cp .env .env.example
```

Then edit `.env.example` to show the structure:
```
GOOGLE_API_KEY=your-google-gemini-api-key-here
COLLEGE_WEBSITE_URL=https://yourcollege.edu
SERPER_API_KEY=your-serper-api-key-here
PUSHOVER_TOKEN=your-pushover-token
PUSHOVER_USER=your-pushover-user
```

This helps users know what environment variables they need.

