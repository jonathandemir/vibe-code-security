#!/bin/bash
set -e

echo "🔒 Starting VibeGuard Repository Scan..."

# Ensure zip and jq are installed (usually available on GitHub ubuntu runners, but good to ensure or assume they exist)
# For the sake of this action, we assume they exist on ubuntu-latest runners.

ZIP_FILE="vibeguard_repo.zip"
echo "📦 Packaging repository (excluding .git and node_modules)..."

# We need to extract the files changed in this push/PR
echo "🔍 Identifying changed files via git diff..."
git config --global --add safe.directory "$GITHUB_WORKSPACE" || true

CHANGED_FILES=""
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
    BASE_SHA=$(jq -r .pull_request.base.sha "$GITHUB_EVENT_PATH")
    CHANGED_FILES=$(git diff --name-only --diff-filter=ACMR "$BASE_SHA" HEAD || true)
else
    # Push event
    BASE_SHA=$(jq -r .before "$GITHUB_EVENT_PATH")
    if [ "$BASE_SHA" == "0000000000000000000000000000000000000000" ] || [ -z "$BASE_SHA" ]; then
        # Handle first push to a new branch, fallback to just latest commit
        CHANGED_FILES=$(git diff --name-only --diff-filter=ACMR HEAD~1 HEAD || true)
    else
        CHANGED_FILES=$(git diff --name-only --diff-filter=ACMR "$BASE_SHA" HEAD || true)
    fi
fi

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️ No supported files changed. Skipping scan or analyzing full repo fallback."
    # Backwards compatibility: if we can't get diff, zip the whole repo excluding junk
    zip -r "$ZIP_FILE" . -x "*.git*" -x "*node_modules*" -x "*venv*" -x "*.venv*" > /dev/null
else
    echo "📦 Packaging only the modified files for ultra-fast scanning..."
    # Ensure files still exist before zipping to avoid zip errors
    FILES_TO_ZIP=""
    for file in $CHANGED_FILES; do
        if [ -f "$file" ]; then
            FILES_TO_ZIP="$FILES_TO_ZIP $file"
        fi
    done
    
    if [ -z "$FILES_TO_ZIP" ]; then
        echo "No valid files to zip (possibly only deletions). Exiting with pure 100 score."
        echo "{\"score\": 100, \"summary\": \"No valid files added or modified.\", \"issues\": []}" > mock_response.json
        RESPONSE=$(cat mock_response.json)
        HTTP_STATUS=0
        # Skip actual upload and skip creating the zip
        SKIP_UPLOAD=true
    else
        zip "$ZIP_FILE" $FILES_TO_ZIP > /dev/null
    fi
fi

if [ "$SKIP_UPLOAD" != "true" ] && [ ! -f "$ZIP_FILE" ]; then
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

# Create a Markdown summary file
OUTPUT_MD="vibeguard_report.md"

echo "# 🛡️ VibeGuard Security Scan" > $OUTPUT_MD
echo "**Score:** $SCORE / 100" >> $OUTPUT_MD
echo "**Summary:** $SUMMARY" >> $OUTPUT_MD
echo "" >> $OUTPUT_MD

# Parse issues and add to summary
ISSUES_COUNT=$(echo "$RESPONSE" | jq -e '.issues | length' || echo 0)

if [ "$ISSUES_COUNT" -eq 0 ]; then
    echo "✅ No vulnerabilities detected. Vibe-Check passed!" >> $OUTPUT_MD
else
    echo "### ⚠️ Findings" >> $OUTPUT_MD
    for ((i=0; i<$ISSUES_COUNT; i++)); do
        TITLE=$(echo "$RESPONSE" | jq -r ".issues[$i].title")
        SEVERITY=$(echo "$RESPONSE" | jq -r ".issues[$i].severity")
        FILE=$(echo "$RESPONSE" | jq -r ".issues[$i].file // \"unknown\"")
        DESC=$(echo "$RESPONSE" | jq -r ".issues[$i].description")
        HOWTO=$(echo "$RESPONSE" | jq -r ".issues[$i].how_to_fix")
        FIX=$(echo "$RESPONSE" | jq -r ".issues[$i].fixed_code_snippet")
        
        echo "#### $TITLE ($SEVERITY) in \`$FILE\`" >> $OUTPUT_MD
        echo "$DESC" >> $OUTPUT_MD
        echo "**Fix Strategy:** $HOWTO" >> $OUTPUT_MD
        
        if [ "$FIX" != "null" ] && [ -n "$FIX" ]; then
            echo "\`\`\`" >> $OUTPUT_MD
            echo "$FIX" >> $OUTPUT_MD
            echo "\`\`\`" >> $OUTPUT_MD
        else
            echo "*(Automated code fixes are a premium feature or require manual intervention)*" >> $OUTPUT_MD
        fi
        echo "---" >> $OUTPUT_MD
    done
fi

# Write to GitHub Actions Summary UI
cat $OUTPUT_MD >> $GITHUB_STEP_SUMMARY

# Post PR Comment if applicable
if [ "$GITHUB_EVENT_NAME" == "pull_request" ] && [ -n "$GITHUB_TOKEN" ]; then
    echo "💬 Posting comment to Pull Request..."
    export GH_TOKEN="$GITHUB_TOKEN"
    PR_NUMBER=$(jq --raw-output .pull_request.number "$GITHUB_EVENT_PATH")
    gh pr comment "$PR_NUMBER" --body-file "$OUTPUT_MD" || echo "⚠️ Failed to post PR comment. Does the GITHUB_TOKEN have pull-requests: write permission?"
fi

# Clean up
rm -f "$OUTPUT_MD"

# Fail the action if the score is below threshold (90)
if [ "$SCORE" -lt 90 ]; then
    echo "❌ Security score ($SCORE) is below 90. Failing the build pipeline."
    exit 1
fi
exit 0
