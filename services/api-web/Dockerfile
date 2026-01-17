FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart

COPY app.py /app/
COPY templates/ /app/templates/
COPY static/ /app/static/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
