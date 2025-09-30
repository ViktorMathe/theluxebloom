#!/bin/bash
# Cleanup script for macOS ghost files in Git repos

echo "🚮 Removing macOS ghost files from working directory..."
find . -name ".DS_Store" -delete
find . -name "._*" -delete

echo "🧹 Removing macOS ghost files from Git history..."
git filter-repo --path-glob ".DS_Store" --invert-paths
git filter-repo --path-glob "._*" --invert-paths

echo "✅ Running garbage collection..."
git gc --prune=now --aggressive

echo "📤 Force pushing cleaned repo to GitHub..."
git push origin --force --all
git push origin --force --tags

echo "✨ Cleanup complete!"