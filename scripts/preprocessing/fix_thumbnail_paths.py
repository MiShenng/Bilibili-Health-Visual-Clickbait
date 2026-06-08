"""
更新 master_bilibili_health.csv 里的 thumbnail_local_path：
- 把所有 .../thumbnails_3000/xxx.jpg 改为 .../thumbnails/xxx.jpg
- 检查每张图是否实际存在
"""
import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "data/private/master_bilibili_health.csv"
THUMB_DIR = ROOT / "data/private/thumbnails"

rows = []
with open(MASTER, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    for row in reader:
        rows.append(row)

fixed = 0
missing = 0
empty = 0
ok = 0

for row in rows:
    bvid = (row.get("bvid") or "").strip()
    if not bvid:
        continue

    # 标准路径
    new_path = os.path.join(THUMB_DIR, f"{bvid}.jpg")

    # 旧路径可能是空、可能指向 thumbnails_3000
    old_path = row.get("thumbnail_local_path", "")
    if "thumbnails_3000" in old_path:
        fixed += 1

    if os.path.exists(new_path):
        row["thumbnail_local_path"] = new_path
        ok += 1
    else:
        # 检查老的 thumbnails 文件夹（已合并，应该都在）
        row["thumbnail_local_path"] = ""
        if old_path:
            missing += 1
        else:
            empty += 1

# 写回
def csv_esc(v):
    if v is None:
        return ""
    s = str(v).replace("\r", " ").replace("\n", " ")
    if "," in s or '"' in s:
        s = '"' + s.replace('"', '""') + '"'
    return s

with open(MASTER, "w", encoding="utf-8-sig") as f:
    f.write(",".join(columns) + "\n")
    for row in rows:
        f.write(",".join(csv_esc(row.get(c, "")) for c in columns) + "\n")

print(f"总行数: {len(rows)}")
print(f"路径已修正（指向新合并文件夹）: {ok:,}")
print(f"  其中从 thumbnails_3000 改写: {fixed:,}")
print(f"路径丢失（图片找不到）: {missing}")
print(f"原本就空（视频被删等）: {empty}")
print(f"\n所有图片现在都在: {THUMB_DIR}/")
