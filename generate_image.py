import os
import base64
import requests
import json
from pathlib import Path
from datetime import datetime

XAI_API_KEY = os.getenv('XAI_API_KEY', '')
XAI_API_URL = 'https://api.x.ai/v1/images/generations'

def enhance_prompt_for_3d(prompt: str) -> str:
    """
    Enhance user prompt for better 3D model generation.
    Adds modifiers that help image-to-3D models like TripoSR.
    """
    # 3D-friendly prompt modifiers
    modifiers = [
        "Professional product photography",
        "isolated on neutral background",
        "full object visible, not cropped",
        "centered composition",
        "studio lighting with soft shadows",
        "multiple angle illumination",
        "clean and simple background",
        "no frames or borders",
        "high detail for 3D reconstruction",
        "sharp focus on the entire object"
    ]

    # Build enhanced prompt
    enhanced = f"{prompt}, {', '.join(modifiers)}"
    return enhanced

def generate_image(prompt: str, output_dir: str = 'jobs') -> str:
    """Generate image using xAI Grok API and save to file."""
    headers = {
        'Authorization': f'Bearer {XAI_API_KEY}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    # Enhance prompt for better 3D generation
    enhanced_prompt = enhance_prompt_for_3d(prompt)

    payload = {
        'model': 'grok-2-image-1212',
        'prompt': enhanced_prompt,
        'n': 1,
        'response_format': 'b64_json'
    }
    
    try:
        response = requests.post(XAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()

        if 'data' in result and len(result['data']) > 0:
            image_data = result['data'][0]['b64_json']
            revised_prompt = result['data'][0].get('revised_prompt', enhanced_prompt)
            
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
