"""單頁 OCR 品質探針；輸出未校對，不能直接成為正式中文資料。"""

import json
import sys
from pathlib import Path

from paddleocr import PaddleOCR


def create_ocr():
    return PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False,
                use_textline_orientation=False, device="cpu",
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="PP-OCRv5_mobile_rec",
                text_recognition_batch_size=1,
                text_det_limit_side_len=1600, text_det_limit_type="max",
                enable_mkldnn=False, cpu_threads=2)

if __name__ == "__main__":
    image, output = sys.argv[1:3]
    Path(output).mkdir(parents=True, exist_ok=True)
    ocr = create_ocr()
    print("模型已載入，開始單頁辨識", flush=True)
    for index, result in enumerate(ocr.predict(image)):
        result.save_to_json(output)
        result.save_to_img(output)
        payload = result.json
        Path(output, f"sample-{index}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print("未校對 OCR 已輸出", output, flush=True)
