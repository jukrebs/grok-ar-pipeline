import os
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = sys.stdin.read().strip()
        if not prompt:
            print('Error: No prompt provided', file=sys.stderr)
            sys.exit(1)

    job_id = sys.argv[2] if len(sys.argv) > 2 else 'default'

    from openai import OpenAI
    import base64

    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        print('Error: XAI_API_KEY not set', file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url='https://api.x.ai/v1')

    try:
        response = client.images.generate(
            model='grok-2-image-1212',
            prompt=prompt,
            n=1,
            response_format='b64_json'
        )

        image_data = response.data[0].b64_json
        revised_prompt = response.data[0].revised_prompt

        output_dir = Path(f'/data/jobs/{job_id}')
        output_dir.mkdir(parents=True, exist_ok=True)

        image_path = output_dir / 'image.jpg'
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        status = {
            'status': 'complete',
            'image_path': str(image_path),
            'revised_prompt': revised_prompt,
            'job_id': job_id
        }
        print(json.dumps(status))

    except Exception as e:
        error_status = {
            'status': 'error',
            'error': str(e),
            'job_id': job_id
        }
        print(json.dumps(error_status))
        sys.exit(1)

if __name__ == '__main__':
    main()
