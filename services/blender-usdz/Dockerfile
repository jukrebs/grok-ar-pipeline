FROM ubuntu:22.04

WORKDIR /app

# Install dependencies (split to avoid truncation issues)
RUN apt-get update
RUN apt-get install -y wget git python3 python3-pip libx11-6 libxi6 libxrender1
RUN apt-get install -y libxrandr2 libxcursor1 libxinerama1 libgl1-mesa-glx
RUN apt-get install -y libglu1-mesa libxext6 libxfixes3 libxxf86vm1 xdg-utils
RUN apt-get install -y && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/pdxor/Glb-to-Usdz-Blender.git /app/blender-usdz

RUN wget -q https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz
RUN tar -xf blender-4.2.0-linux-x64.tar.xz
RUN mv blender-4.2.0-linux-x64 /usr/local/blender
RUN rm blender-4.2.0-linux-x64.tar.xz

COPY export_usdz.py /app/
COPY convert.py /app/
RUN chmod +x /app/export_usdz.py /app/convert.py

WORKDIR /app

CMD ["sleep", "infinity"]
