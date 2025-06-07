#!/bin/bash

# Get the staged changes
DIFF=$(git diff)

# If no changes are staged, exit
if [ -z "$DIFF" ]; then
    echo "No changes staged for commit"
    exit 1
fi

# Generate commit message using ollama
COMMIT_MSG=$(echo "Based on this git diff, write a clear and concise commit message that follows conventional commit format (type: subject). The message should be in present tense and describe what the changes do.

$DIFF" | ollama run gemma3:1b)

# Print the generated message
echo "Generated commit message:"
echo "------------------------"
echo "$COMMIT_MSG"
echo "------------------------"

# Return the message for use in git commit
echo "$COMMIT_MSG" 