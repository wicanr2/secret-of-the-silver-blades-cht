#!/usr/bin/env python3
"""G9 HD 主題同步（#10）：把 workplace/hd/theme 的 JSON 與它們實際引用的 PNG、.idx 複製到 repo 的 hd/theme/，
逐檔核對 SHA-256；沒被引用的舊檔不帶。在 sosb-img 容器內以 python3 -I 執行。目標目錄先清空再寫。"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, type=Path)
    ap.add_argument('--dst', required=True, type=Path)
    a = ap.parse_args()
    files = {}
    for j in sorted(a.src.glob('*.json')):
        m = json.loads(j.read_text())
        rows = m.get('items', []) + m.get('heads', []) + m.get('bodies', []) + m.get('assets', [])
        for r in rows:
            for f, h in (('png', 'png_sha256'), ('indexed', 'indexed_sha256' if 'indexed_sha256' in r else 'idx_sha256')):
                if f in r:
                    files[r[f]] = r.get(h)
        files[j.name] = None
    if a.dst.exists():
        shutil.rmtree(a.dst)
    for name, want in sorted(files.items()):
        src = a.src / name
        if want and sha(src) != want:
            sys.exit(f'{name}：雜湊與主題 JSON 不符')
        (a.dst / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, a.dst / name)
    print('同步', len(files), '檔')


if __name__ == '__main__':
    main()
