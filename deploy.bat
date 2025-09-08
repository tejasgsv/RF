@echo off
echo 🚀 Deploying to GitHub Pages...

echo Step 1: Adding files...
git add index.html _config.yml GITHUB_HOSTING.md

echo Step 2: Committing changes...
git commit -m "Deploy website to GitHub Pages"

echo Step 3: Pushing to GitHub...
git push origin master

echo ✅ Deployment complete!
echo 🌐 Website will be live at: https://yourusername.github.io/reliance-ai-platform
echo ⏱️ Wait 5-10 minutes for GitHub Pages to build

pause