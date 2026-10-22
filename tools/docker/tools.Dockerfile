# 盤點、解壓、PDF 轉文字與下載工具（PKZIP implode 需 Info-ZIP unzip；RAR 4 用 unar）。
FROM debian@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 unzip unar poppler-utils curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
