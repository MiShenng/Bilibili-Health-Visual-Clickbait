"""
Compute CLIP cosine similarity between video thumbnail and title.
Uses open_clip (no transformers dependency).
Outputs: output/bilibili_health_clean_clip.csv  (adds column: clip_sim)
"""
import csv
import os
import time

import torch
import open_clip
from PIL import Image

SRC = "output/bilibili_health_clean.csv"
OUT = "output/bilibili_health_clean_clip.csv"
THUMB_DIR = "output/thumbnails"
MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"
BATCH_SIZE = 128
LOG_EVERY = 1000

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {DEVICE}")

print(f"Loading model {MODEL_NAME} ({PRETRAINED}) ...")
model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
tokenizer = open_clip.get_tokenizer(MODEL_NAME)
model = model.to(DEVICE)
model.eval()


def find_thumb(bvid: str) -> str | None:
    p = os.path.join(THUMB_DIR, f"{bvid}.jpg")
    return p if os.path.exists(p) and os.path.getsize(p) > 0 else None


def compute_batch(bvids: list, titles: list) -> list:
    images = []
    for bvid in bvids:
        p = find_thumb(bvid)
        try:
            img = preprocess(Image.open(p).convert("RGB")) if p else preprocess(Image.new("RGB", (224, 224)))
        except Exception:
            img = preprocess(Image.new("RGB", (224, 224)))
        images.append(img)

    img_tensor = torch.stack(images).to(DEVICE)
    text_tokens = tokenizer(titles, context_length=77).to(DEVICE)

    with torch.no_grad():
        img_emb = model.encode_image(img_tensor)
        txt_emb = model.encode_text(text_tokens)
        img_emb = img_emb / img_emb.norm(dim=-1, keepdim=True)
        txt_emb = txt_emb / txt_emb.norm(dim=-1, keepdim=True)
        sims = (img_emb * txt_emb).sum(dim=-1).cpu().tolist()
    return sims


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
    N = len(rows)
    print(f"Processing {N} videos ...")

    fieldnames = list(rows[0].keys()) + ["clip_sim"]
    t0 = time.time()
    results = []

    for i in range(0, N, BATCH_SIZE):
        batch = rows[i: i + BATCH_SIZE]
        bvids = [r["bvid"] for r in batch]
        titles = [r.get("title", "") or "" for r in batch]
        sims = compute_batch(bvids, titles)
        for r, s in zip(batch, sims):
            rec = dict(r)
            rec["clip_sim"] = f"{s:.6f}"
            results.append(rec)

        done = min(i + BATCH_SIZE, N)
        if done % LOG_EVERY < BATCH_SIZE or done == N:
            elapsed = time.time() - t0
            eta = elapsed / done * (N - done) if done < N else 0
            print(f"  {done}/{N}  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    with open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    elapsed = time.time() - t0
    print(f"\nDone. {N} rows -> {OUT}  ({elapsed:.0f}s total)")

    sims = sorted(float(r["clip_sim"]) for r in results)
    n = len(sims)
    print(f"\nclip_sim distribution:")
    print(f"  mean   = {sum(sims)/n:.4f}")
    print(f"  median = {sims[n//2]:.4f}")
    print(f"  P10    = {sims[int(0.1*n)]:.4f}")
    print(f"  P25    = {sims[n//4]:.4f}")
    print(f"  P75    = {sims[3*n//4]:.4f}")
    print(f"  P90    = {sims[int(0.9*n)]:.4f}")
    print(f"  min    = {sims[0]:.4f}")
    print(f"  max    = {sims[-1]:.4f}")


if __name__ == "__main__":
    main()
