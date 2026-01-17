import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title='Grok Pipeline API')

app.mount('/static', StaticFiles(directory='static'), name='static')

DATA_DIR = Path('/data/jobs')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Pre-populate examples as complete jobs
examples = [
    'ex_elon-figurine',
    'ex_mars-habitat',
    'ex_xai-robot',
]

jobs = {
    ex_id: {
        'job_id': ex_id,
        'status': 'complete',
        'stage': 'complete',
        'progress': 100,
        'created_at': None,
        'prompt': 'Pre-rendered example',
    }
    for ex_id in examples
}

class GenerateRequest(BaseModel):
    prompt: str

@app.get('/')
async def root():
    return HTMLResponse(open('/app/templates/index.html').read())

@app.post('/api/generate')
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    jobs[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'stage': 'initializing',
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'prompt': request.prompt,
    }

    background_tasks.add_task(run_pipeline, job_id, request.prompt)
    return {'job_id': job_id, 'status': 'queued'}

@app.get('/api/status/{job_id}')
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail='Job not found')
    return jobs[job_id]

@app.get('/api/examples')
async def get_examples():
    """Return list of pre-rendered example jobs"""
    examples = [
        {
            'job_id': 'ex_elon-figurine',
            'name': 'Elon Figurine',
            'description': 'Collectible Elon Musk figurine with premium quality design',
            'image_url': '/api/asset/ex_elon-figurine?asset_type=image',
        },
        {
            'job_id': 'ex_mars-habitat',
            'name': 'Mars Globe',
            'description': 'Photorealistic Mars planet as a printable desk globe, 15cm diameter sphere with Valles Marineris canyon, polar ice caps, and craters',
            'image_url': '/api/asset/ex_mars-habitat?asset_type=image',
        },
        {
            'job_id': 'ex_xai-robot',
            'name': 'xAI Lobby Robot',
            'description': 'Photorealistic xAI lobby robot statue as desk model, sleek humanoid on black pedestal with glowing blue LED accents',
            'image_url': '/api/asset/ex_xai-robot?asset_type=image',
        },
    ]
    return {'examples': examples}

@app.get('/api/asset/{job_id}')
async def get_asset(job_id: str, asset_type: str = 'usdz'):
    job_dir = DATA_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail='Job not found')

    if asset_type == 'usdz':
        file_path = job_dir / 'model.usdz'
    elif asset_type == 'glb':
        file_path = job_dir / 'model.glb'
    elif asset_type == 'image':
        file_path = job_dir / 'image.jpg'
    else:
        raise HTTPException(status_code=400, detail='Invalid asset type')

    if not file_path.exists():
        raise HTTPException(status_code=404, detail='Asset not found')

    return FileResponse(
        path=str(file_path),
        media_type='application/octet-stream',
        filename=file_path.name,
    )

async def run_pipeline(job_id: str, prompt: str):
    try:
        update_job(job_id, 'generating_image', 10)
        await run_container('grok-image', job_id, prompt)

        update_job(job_id, 'generating_3d', 50)
        await run_container('triposr', job_id)

        update_job(job_id, 'converting_usdz', 80)
        await run_container('blender-usdz', job_id)

        update_job(job_id, 'complete', 100)

    except Exception as e:
        update_job(job_id, 'error', 0, str(e))


def update_job(job_id: str, stage: str, progress: int, error: Optional[str] = None):
    if job_id in jobs:
        jobs[job_id].update({
            'status': 'error' if error else ('complete' if stage == 'complete' else 'processing'),
            'stage': stage,
            'progress': progress,
            'error': error,
        })

async def run_container(container_name: str, job_id: str, prompt: Optional[str] = None):
    cmd = ['docker', 'exec', container_name]

    if container_name == 'grok-image':
        cmd.extend(['python3', '/app/generate.py', prompt, job_id])
    elif container_name == 'triposr':
        cmd.extend(['/app/run.sh', job_id])
    elif container_name == 'blender-usdz':
        cmd.extend(['/usr/local/blender/blender', '-b', '-P', '/app/export_usdz.py', '--', '/data/jobs/{}/model.glb'.format(job_id), '/data/jobs/{}/model.usdz'.format(job_id), job_id])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f'{container_name} failed: {stderr.decode()}')

    return stdout.decode()
