"""本機研究用批次 OCR。保留原始區塊順序與座標，所有頁面標記為未校對。"""

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path

from ocr_sample import create_ocr


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
if not args.input.is_dir():
    raise SystemExit("輸入目錄不存在")
args.output.mkdir(parents=True, exist_ok=True)
sources = sorted(p for p in args.input.rglob("*")
                 if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg"))
cache = Path.home() / ".paddlex/official_models"
models = {}
for name in ("PP-OCRv5_mobile_det", "PP-OCRv5_mobile_rec"):
    directory = cache / name
    if not directory.is_dir():
        raise SystemExit(f"缺少已下載的模型：{name}")
    models[name] = {str(p.relative_to(directory)): sha(p)
                    for p in sorted(directory.rglob("*")) if p.is_file()}
provenance = {"schema": 1, "status": "OCR draft, not proofread",
              "packages": {p: importlib.metadata.version(p) for p in
                           ("paddleocr", "paddlepaddle", "paddlex", "Pillow")},
              "tool_sha256": {p: sha(Path(__file__).parent / p)
                              for p in ("ocr_batch.py", "ocr_sample.py")},
              "models": models, "image_id": os.environ.get("DQK_IMAGE_ID", "unknown")}
identity = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
(args.output / "provenance.json").write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
ocr = create_ocr()
records = []
errors = 0
for index, source in enumerate(sources, 1):
    relative = source.relative_to(args.input)
    if source.resolve().is_relative_to(args.input.resolve()) is False:
        raise ValueError("來源連結超出輸入目錄")
    target = args.output / relative.parent / (source.name + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha(source)
    record = {"source": str(relative), "source_sha256": source_hash,
              "identity": identity, "status": "OCR draft, not proofread"}
    try:
        existing = json.loads(target.read_text()) if target.exists() else {}
        if existing.get("source_sha256") == source_hash and existing.get("identity") == identity:
            payload = existing
        else:
            results = list(ocr.predict(str(source)))
            if len(results) != 1:
                raise ValueError("單張圖片預期一個辨識結果")
            result = results[0].json["res"]
            payload = dict(record, result=result)
            target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            del results
        record["regions"] = len(payload["result"]["rec_texts"])
        record["output"] = str(target.relative_to(args.output))
        record["output_sha256"] = sha(target)
    except Exception as error:
        errors += 1
        record.update(status="error", error=f"{type(error).__name__}: {error}")
    records.append(record)
    (args.output / "manifest.json").write_text(json.dumps(
        {"schema": 1, "complete": index == len(sources), "sources": len(sources),
         "processed": index, "errors": errors, "pages": records},
        ensure_ascii=False, indent=2) + "\n")
    print(f"{index}/{len(sources)} {relative} {record['status']}", flush=True)
    gc.collect()
raise SystemExit(1 if errors else 0)
