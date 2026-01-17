FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir requests openai

COPY generate.py /app/
COPY run.sh /app/

RUN chmod +x /app/run.sh

ENV XAI_API_KEY=${XAI_API_KEY}

CMD ["sleep", "infinity"]
