"""G1 原始輸入盤點：外層 zip 與內層 PKSFX 的雜湊、成員清單、解壓與逐檔雜湊。

用法（Docker sosb-tools 內）：python3 -I tools/inventory.py <外層 zip> <輸出根>
外層 zip 是安裝器發行（install.com＋secret1.exe＋secret2.exe）。install.com 的字串引用兩個
PKSFX 檔名；這裡以 Info-ZIP unzip 把兩者展開到 <輸出根>/dos/sosb/，同名成員視為衝突。
"""
import hashlib, json, subprocess, sys, zipfile
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
def sha(b): return hashlib.sha256(b).hexdigest()
def members(z):
    return [{"name": i.filename, "size": i.file_size, "crc": f"{i.CRC:08x}",
             "date": "%04d-%02d-%02d %02d:%02d" % i.date_time[:5]} for i in z.infolist()]

game = out / "dos" / "sosb"
game.mkdir(parents=True, exist_ok=True)
report = {"archive": src.name, "sha256": sha(src.read_bytes()), "sfx": []}
with zipfile.ZipFile(src) as outer:
    report["members"] = members(outer)
    seen = {}
    for name in ("secret1.exe", "secret2.exe"):
        data = outer.read(name)
        sfx_path = out / "zip" / name
        sfx_path.parent.mkdir(parents=True, exist_ok=True)
        sfx_path.write_bytes(data)
        with zipfile.ZipFile(sfx_path) as z:
            report["sfx"].append({"name": name, "sha256": sha(data), "members": members(z)})
            for i in z.infolist():
                key = i.filename.upper()
                if key in seen:
                    raise SystemExit(f"成員衝突：{i.filename} 同時在 {seen[key]} 與 {name}")
                seen[key] = name
        # PKZIP 1.x 的 implode 方法 zipfile 不支援，改用 Info-ZIP unzip（sosb-tools image）。
        subprocess.run(["unzip", "-q", "-n", str(sfx_path), "-d", str(game)], check=True)
files = [{"path": str(p.relative_to(game)), "size": p.stat().st_size, "sha256": sha(p.read_bytes())}
         for p in sorted(game.rglob("*")) if p.is_file()]
report["files"] = files
json.dump(report, open(out / "inventory.json", "w"), ensure_ascii=False, indent=1)
print(src.name, report["sha256"])
for s in report["sfx"]: print(s["name"], s["sha256"], len(s["members"]), "members")
for f in files: print(f"{f['size']:>8} {f['sha256'][:16]} {f['path']}")
