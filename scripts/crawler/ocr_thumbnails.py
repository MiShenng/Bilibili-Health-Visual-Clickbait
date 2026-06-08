"""
OCR thumbnail images to extract text overlay features.
Outputs per-video:
  - ocr_text        : all detected text joined
  - ocr_char_count  : number of characters detected
  - ocr_word_count  : number of tokens detected
  - ocr_text_ratio  : text area / image area (proxy for text prominence)
  - ocr_has_text    : bool, any text found
  - ocr_max_conf    : max detection confidence

Saves: output/bilibili_health_clean_ocr.csv
"""
import csv
import os
import time
import numpy as np
from PIL import Image
import easyocr

SRC        = "output/bilibili_health_clean_clip.csv"
OUT        = "output/bilibili_health_clean_ocr.csv"
THUMB_DIR  = "output/thumbnails"
LOG_EVERY  = 200
SAMPLE_N   = 3000   # random sample; set None to run all
RANDOM_SEED = 42

print("Initialising EasyOCR (ch_sim + en) ...")
reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
print("Ready.")


def find_thumb(bvid: str) -> str | None:
    p = os.path.join(THUMB_DIR, f"{bvid}.jpg")
    return p if os.path.exists(p) and os.path.getsize(p) > 0 else None


def ocr_image(path: str) -> dict:
    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        img_area = w * h

        results = reader.readtext(path, detail=1)

        texts = []
        text_area = 0.0
        confs = []

        for (bbox, text, conf) in results:
            texts.append(text.strip())
            confs.append(conf)
            # bbox is [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            box_area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            text_area += box_area

        joined = " ".join(texts)
        return {
            "ocr_text":       joined,
            "ocr_char_count": len(joined.replace(" ", "")),
            "ocr_word_count": len(texts),
            "ocr_text_ratio": round(text_area / img_area, 4) if img_area > 0 else 0.0,
            "ocr_has_text":   len(texts) > 0,
            "ocr_max_conf":   round(max(confs), 4) if confs else 0.0,
        }
    except Exception as e:
        return {
            "ocr_text": "", "ocr_char_count": 0, "ocr_word_count": 0,
            "ocr_text_ratio": 0.0, "ocr_has_text": False, "ocr_max_conf": 0.0,
        }


def main():
    import random
    all_rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
    if SAMPLE_N and SAMPLE_N < len(all_rows):
        random.seed(RANDOM_SEED)
        rows = random.sample(all_rows, SAMPLE_N)
        print(f"Random sample: {SAMPLE_N} / {len(all_rows)} total")
    else:
        rows = all_rows
    N = len(rows)
    print(f"Processing {N} thumbnails ...")

    new_cols = ["ocr_text","ocr_char_count","ocr_word_count",
                "ocr_text_ratio","ocr_has_text","ocr_max_conf"]
    fieldnames = list(rows[0].keys()) + new_cols

    t0 = time.time()
    results = []

    for i, row in enumerate(rows):
        bvid = row.get("bvid", "")
        path = find_thumb(bvid)
        ocr  = ocr_image(path) if path else {c: "" for c in new_cols}

        rec = dict(row)
        rec.update(ocr)
        results.append(rec)

        if (i + 1) % LOG_EVERY == 0 or (i + 1) == N:
            elapsed = time.time() - t0
            eta = elapsed / (i + 1) * (N - i - 1)
            print(f"  {i+1}/{N}  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

            # checkpoint
            with open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                w.writerows(results)

    elapsed = time.time() - t0
    print(f"\nDone. {N} rows -> {OUT}  ({elapsed:.0f}s total)")

    # summary stats
    has_text = sum(1 for r in results if str(r.get("ocr_has_text","")).upper() in ("TRUE","1"))
    ratios   = [float(r.get("ocr_text_ratio", 0)) for r in results]
    chars    = [int(r.get("ocr_char_count", 0)) for r in results]
    print(f"\nOCR Summary:")
    print(f"  Has text overlay:  {has_text} / {N}  ({has_text/N:.1%})")
    print(f"  text_ratio  mean={np.mean(ratios):.4f}  median={np.median(ratios):.4f}  P75={np.percentile(ratios,75):.4f}")
    print(f"  char_count  mean={np.mean(chars):.1f}   median={np.median(chars):.0f}   P75={np.percentile(chars,75):.0f}")


if __name__ == "__main__":
    main()
