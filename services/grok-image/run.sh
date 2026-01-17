#!/bin/bash

# Wait for prompt file or run directly
if [ -f /data/jobs/PROMPT ]; then
    JOB_ID=$(cat /data/jobs/PROMPT | jq -r '.job_id // empty')
    PROMPT=$(cat /data/jobs/PROMPT | jq -r '.prompt // empty')
    
    if [ -n "$PROMPT" ]; then
        python3 /app/generate.py "$PROMPT" "$JOB_ID"
    else
        echo 'No prompt found' >&2
        exit 1
    fi
else
    # Run directly with arguments if provided
    python3 /app/generate.py "$@"
fi
