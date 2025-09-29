#!/bin/bash
# Branch Social Listening Scraper - GitHub Setup Script

echo "🚀 Branch Social Listening Scraper - GitHub Setup"
echo "================================================="
echo ""

# Check if git remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Git remote 'origin' already configured"
    git remote -v
else
    echo "❓ Please enter your GitHub repository URL:"
    echo "   Format: https://github.com/USERNAME/REPOSITORY.git"
    echo ""
    read -p "GitHub Repository URL: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ Error: Repository URL cannot be empty"
        exit 1
    fi
    
    echo ""
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$REPO_URL"
    echo "✅ Remote added successfully"
fi

echo ""
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Successfully pushed to GitHub!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to your GitHub repository"
    echo "2. Follow the detailed setup guide: GITHUB_ACTIONS_SETUP.md"  
    echo "3. Configure GitHub secrets for Google Sheets and Slack"
    echo "4. Test the workflow manually in GitHub Actions"
    echo ""
    echo "📚 For detailed instructions, see:"
    echo "   - GITHUB_ACTIONS_SETUP.md (comprehensive guide)"
    echo "   - README.md (quick start)"
else
    echo ""
    echo "❌ Error pushing to GitHub"
    echo "💡 Common solutions:"
    echo "   - Verify repository URL is correct"
    echo "   - Check GitHub authentication (token/SSH key)"
    echo "   - Ensure repository exists and you have push access"
    echo ""
    echo "🔧 Manual commands:"
    echo "   git remote add origin YOUR_REPO_URL"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi
