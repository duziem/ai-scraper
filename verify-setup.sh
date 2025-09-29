#!/bin/bash
# Branch Social Listening Scraper - Setup Verification Script

echo "🔍 Branch Social Listening Scraper - Setup Verification"
echo "===================================================="
echo ""

# Check Python version
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found"
    exit 1
fi

# Check virtual environment
echo ""
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment exists"
else
    echo "   ❌ Virtual environment not found"
    echo "   💡 Run: python3 -m venv venv"
fi

# Check requirements file
echo ""
echo "3. Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    PACKAGE_COUNT=$(wc -l < requirements.txt | tr -d ' ')
    echo "   ✅ requirements.txt exists ($PACKAGE_COUNT lines)"
else
    echo "   ❌ requirements.txt not found"
fi

# Check project structure
echo ""
echo "4. Checking project structure..."
REQUIRED_DIRS=("scrapers" "analyze" "store" "alerts" ".github/workflows")
MISSING_DIRS=()

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/ exists"
    else
        echo "   ❌ $dir/ missing"
        MISSING_DIRS+=("$dir")
    fi
done

# Check key files
echo ""
echo "5. Checking key files..."
REQUIRED_FILES=("run_all.py" "README.md" "config_example.env" ".github/workflows/run.yml" "GITHUB_ACTIONS_SETUP.md")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file missing"
        MISSING_FILES+=("$file")
    fi
done

# Check git status
echo ""
echo "6. Checking git repository..."
if [ -d ".git" ]; then
    echo "   ✅ Git repository initialized"
    
    # Check for commits
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        COMMIT_COUNT=$(git rev-list --all --count)
        echo "   ✅ Repository has commits ($COMMIT_COUNT)"
    else
        echo "   ⚠️  No commits yet"
    fi
    
    # Check for remote
    if git remote get-url origin >/dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        echo "   ✅ GitHub remote configured: $REMOTE_URL"
    else
        echo "   ⚠️  No GitHub remote configured"
        echo "   💡 Run: ./push-to-github.sh"
    fi
else
    echo "   ❌ Git repository not initialized"
    echo "   💡 Run: git init"
fi

# Check for sensitive files
echo ""
echo "7. Checking for sensitive files..."
SENSITIVE_PATTERNS=("*.json" ".env" "*credentials*" "*secret*")
SENSITIVE_FOUND=()

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if ls $pattern >/dev/null 2>&1; then
        for file in $pattern; do
            if [ -f "$file" ] && [[ "$file" != "config_example.env" ]]; then
                SENSITIVE_FOUND+=("$file")
            fi
        done
    fi
done

if [ ${#SENSITIVE_FOUND[@]} -eq 0 ]; then
    echo "   ✅ No sensitive files found in repository"
else
    echo "   ⚠️  Sensitive files detected:"
    for file in "${SENSITIVE_FOUND[@]}"; do
        echo "      - $file"
    done
    echo "   💡 Ensure these files are in .gitignore and not committed to git"
fi

# Summary
echo ""
echo "📋 SETUP SUMMARY"
echo "================"

if [ ${#MISSING_DIRS[@]} -eq 0 ] && [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "🎉 Setup is COMPLETE! Ready for GitHub Actions configuration."
    echo ""
    echo "📚 Next steps:"
    echo "   1. Push to GitHub: ./push-to-github.sh"
    echo "   2. Configure secrets: Follow GITHUB_ACTIONS_SETUP.md"
    echo "   3. Test workflow: GitHub repository → Actions tab"
else
    echo "⚠️  Setup is INCOMPLETE. Missing components:"
    
    if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
        echo "   Missing directories: ${MISSING_DIRS[*]}"
    fi
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo "   Missing files: ${MISSING_FILES[*]}"
    fi
    
    echo ""
    echo "💡 Run Stage 1 implementation to create missing components."
fi

echo ""
echo "📖 For detailed instructions, see:"
echo "   - README.md (quick start guide)"
echo "   - GITHUB_ACTIONS_SETUP.md (detailed GitHub setup)"
