FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    ninja-build \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121

COPY ../TripoSR /app/triposr

WORKDIR /app/triposr

RUN pip install --no-cache-dir onnxruntime-gpu onnx -r requirements.txt

COPY services/triposr/run.sh /app/
RUN chmod +x /app/run.sh

WORKDIR /app

CMD ["sleep", "infinity"]
