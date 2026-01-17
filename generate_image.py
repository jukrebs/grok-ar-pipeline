import os
import base64
import requests
import json
from pathlib import Path
from datetime import datetime

XAI_API_KEY = os.getenv('XAI_API_KEY', '')
XAI_API_URL = 'https://api.x.ai/v1/images/generations'

def generate_image(prompt: str, output_dir: str = 'jobs') -> str:
    """Generate image using xAI Grok API and save to file."""
    headers = {
        'Authorization': f'Bearer {XAI_API_KEY}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    
    payload = {
        'model': 'grok-2-image-1212',
        'prompt': prompt,
        'n': 1,
        'response_format': 'b64_json'
    }
    
    try:
        response = requests.post(XAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if 'data' in result and len(result['data']) > 0:
            image_data = result['data'][0]['b64_json']
            revised_prompt = result['data'][0].get('revised_prompt', prompt)
            
            # Decode base64 and save
            image_bytes = base64.b64decode(image_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'image_{timestamp}.jpg'
            filepath = Path(output_dir) / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            print(f'Image saved: {filepath}')
            print(f'Revised prompt: {revised_prompt}')
            return str(filepath)
        else:
            raise Exception(f'No image data in response: {result}')
    
    except Exception as e:
        raise Exception(f'Image generation failed: {e}')

if __name__ == '__main__':
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else 'A cat in a tree'
    generate_image(prompt, 'jobs')
