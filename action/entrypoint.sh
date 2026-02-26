#!/bin/bash
set -e

echo "🔒 Starting VibeGuard Repository Scan..."

# Ensure zip and jq are installed (usually available on GitHub ubuntu runners, but good to ensure or assume they exist)
# For the sake of this action, we assume they exist on ubuntu-latest runners.

ZIP_FILE="vibeguard_repo.zip"
echo "📦 Packaging repository (excluding .git and node_modules)..."

# Zip the current workspace
# Zip the current workspace, excluding sensitive files and directories
zip -r "$ZIP_FILE" . \
    -x "*.git*" \
    -x "*node_modules*" \
    -x "*venv*" \
    -x "*.venv*" \
    -x "*.env*" \
    -x "*id_rsa*" \
    -x "*id_ed25519*" \
    -x "*.pem" \
    -x "*.key" \
    -x "*.p12" \
    -x "*.pfx" \
    -x "*credentials*" \
    -x "*service-account*" \
    -x "*.npmrc" \
    -x "*.pypirc" \
    -x "*.netrc" \
    -x "*__pycache__*" \
    > /dev/null

if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ Failed to create repository archive."
    exit 1
fi

# Ensure API_URL points to /scan-repo if it still points to /scan
# This is a backward-compatibility fix just in case the user didn't update their action.yml
if [[ "$API_URL" == *"/scan" ]]; then
    API_URL="${API_URL}-repo"
fi

echo "📡 Uploading repository to VibeGuard API: $API_URL... (Language: $LANGUAGE)"

# Call the API with multipart/form-data
RESPONSE=$(curl -s -X POST -F "file=@$ZIP_FILE" -F "language=$LANGUAGE" "$API_URL")
HTTP_STATUS=$?

if [ $HTTP_STATUS -ne 0 ]; then
    echo "❌ Failed to connect to VibeGuard API."
    rm -f "$ZIP_FILE"
    exit 1
fi

echo "--- Scan Complete ---"
rm -f "$ZIP_FILE"

# Format the output for GitHub Actions summary
# Use jq to safely parse the response
SCORE=$(echo "$RESPONSE" | jq -r '.score // 0')
SUMMARY=$(echo "$RESPONSE" | jq -r '.summary // "No summary provided."')

echo "🛡️ VibeGuard Security Score: $SCORE / 100"
echo "📝 Summary: $SUMMARY"

# Create a Markdown summary
echo "# 🛡️ VibeGuard Repository Scan Results" >> $GITHUB_STEP_SUMMARY
echo "**Security Score:** $SCORE / 100" >> $GITHUB_STEP_SUMMARY
echo "**Summary:** $SUMMARY" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

# Parse issues and add to summary
ISSUES_COUNT=$(echo "$RESPONSE" | jq -e '.issues | length' || echo 0)

if [ "$ISSUES_COUNT" -eq 0 ]; then
    echo "✅ No vulnerabilities detected!" >> $GITHUB_STEP_SUMMARY
    exit 0
fi

echo "### ⚠️ Findings" >> $GITHUB_STEP_SUMMARY

for ((i=0; i<$ISSUES_COUNT; i++)); do
    TITLE=$(echo "$RESPONSE" | jq -r ".issues[$i].title")
    SEVERITY=$(echo "$RESPONSE" | jq -r ".issues[$i].severity")
    FILE=$(echo "$RESPONSE" | jq -r ".issues[$i].file // \"unknown\"")
    DESC=$(echo "$RESPONSE" | jq -r ".issues[$i].description")
    HOWTO=$(echo "$RESPONSE" | jq -r ".issues[$i].how_to_fix")
    FIX=$(echo "$RESPONSE" | jq -r ".issues[$i].fixed_code_snippet")
    
    echo "#### $TITLE ($SEVERITY) in \`$FILE\`" >> $GITHUB_STEP_SUMMARY
    echo "$DESC" >> $GITHUB_STEP_SUMMARY
    echo "**Fix Strategy:** $HOWTO" >> $GITHUB_STEP_SUMMARY
    
    if [ "$FIX" != "null" ] && [ -n "$FIX" ]; then
        echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
        echo "$FIX" >> $GITHUB_STEP_SUMMARY
        echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
    else
        echo "*(Automated code fixes are a premium VibeGuard feature or require manual intervention here)*" >> $GITHUB_STEP_SUMMARY
    fi
    echo "---" >> $GITHUB_STEP_SUMMARY
done

# Make the action fail if score is below 90
if [ "$SCORE" -lt 90 ]; then
    echo "❌ Security score is below 90. Failing the build."
    exit 1
fi
