#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path

def convert_glb_to_usdz(input_path: str, output_path: str) -> dict:
    """Convert GLB to USDZ using Blender."""
    try:
        # Use Blender in background mode to convert
        cmd = [
            '/usr/local/blender/blender',
            '-b',  # Background mode
            '-P', '/app/blender-usdz/export_as_usdz.py',
            '--',
            input_path,
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            error = result.stderr or result.stdout
            return {
                'status': 'error',
                'error': f'Blender conversion failed: {error}'
            }
        
        # Check if output file exists
        if Path(output_path).exists():
            return {
                'status': 'complete',
                'usdz_path': output_path,
                'size_mb': round(Path(output_path).stat().st_size / (1024*1024), 2)
            }
        else:
            return {
                'status': 'error',
                'error': 'USDZ file not created'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': 'Conversion timed out'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    # Read job_id from argument
    job_id = sys.argv[1] if len(sys.argv) > 1 else 'default'
    
    # Check if GLB exists
    glb_path = Path(f'/data/jobs/{job_id}/model.glb')
    if not glb_path.exists():
        result = {
            'status': 'error',
            'error': 'GLB file not found',
            'job_id': job_id
        }
        print(json.dumps(result))
        sys.exit(1)
    
    # Output path
    usdz_path = f'/data/jobs/{job_id}/model.usdz'
    
    result = convert_glb_to_usdz(str(glb_path), usdz_path)
    result['job_id'] = job_id
    print(json.dumps(result))
    
    sys.exit(0 if result['status'] == 'complete' else 1)

if __name__ == '__main__':
    main()
