#!/bin/bash

JOB_ID=${1:-default}

if [ ! -f "/data/jobs/${JOB_ID}/image.jpg" ]; then
    echo '{status: error, error: Image not found}' >&2
    exit 1
fi

cd /app/triposr

python3 run.py \
    /data/jobs/${JOB_ID}/image.jpg \
    --output-dir /data/jobs/${JOB_ID} \
    --model-save-format glb \
    --device cuda:0 \
    --bake-texture

GLB_FILE=$(find /data/jobs/${JOB_ID}/ -name "*.glb" 2>/dev/null | head -n 1)
if [ -n "$GLB_FILE" ]; then
    mv "$GLB_FILE" /data/jobs/${JOB_ID}/model.glb
    echo '{status: complete, glb_path: /data/jobs/\${JOB_ID}/model.glb, job_id: \${JOB_ID}}'
else
    echo '{status: error, error: GLB generation failed}' >&2
    exit 1
fi
