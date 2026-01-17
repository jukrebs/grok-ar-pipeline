FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y wget git python3 python3-pip \
    libx11-6 libxi6 libxrender1 libxrandr2 libxcursor1 libxinerama1 \
    libgl1-mesa-glx libglu1-mesa libxext6 libxfixes3 libxxf86vm1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/pdxor/Glb-to-Usdz-Blender.git /app/blender-usdz

RUN wget -q https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz \
    && tar -xf blender-4.2.0-linux-x64.tar.xz \
    && mv blender-4.2.0-linux-x64 /usr/local/blender \
    && rm blender-4.2.0-linux-x64.tar.xz

COPY convert.py /app/
RUN chmod +x /app/convert.py

WORKDIR /app

CMD ["sleep", "infinity"]
