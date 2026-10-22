# 影像處理與點陣字型（Pillow）。版本鎖定，沿用克萊恩英豪 tools/docker/img.Dockerfile。
FROM python:3.13-slim
RUN pip install --no-cache-dir pillow==11.0.0 numpy==2.1.3
