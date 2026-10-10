import hashlib
import json
from pathlib import Path

# 整合包根目录（脚本放在这里运行）
ROOT = Path(".").resolve()

# 需要排除的目录和文件（不纳入清单）
EXCLUDE_DIRS = {
    "BepInEx/cache",
    "BepInEx/LogOutput.log",
    ".git",
    "__pycache__",
    "bin",
    "obj",
}
EXCLUDE_FILES = {
    "manifest.json",
    "generate_manifest.py",
    "updater_manifest.json",
    "updater_version.txt",
}

def should_exclude(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    for d in EXCLUDE_DIRS:
        if rel == d or rel.startswith(d + "/"):
            return True
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix in (".log", ".tmp", ".disabled"):
        return True
    return False

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    version = input("请输入新版本号: ").strip()
    if not version:
        print("版本号不能为空")
        return

    print(f"开始扫描目录: {ROOT}")
    all_files = [p for p in ROOT.rglob("*") if p.is_file() and not should_exclude(p)]
    total = len(all_files)
    print(f"共发现 {total} 个文件，开始计算哈希...\n")

    files = []
    for i, path in enumerate(all_files, 1):
        rel = path.relative_to(ROOT).as_posix()
        try:
            sha = compute_sha256(path)
            size = path.stat().st_size
            files.append({"path": rel, "size": size, "sha256": sha})
            print(f"[{i}/{total}] {rel}  ({size} bytes)")
        except Exception as e:
            print(f"[{i}/{total}] 跳过 {rel}: {e}")

    manifest = {"version": version, "files": files}
    out = ROOT / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n已生成 {out}")
    print(f"版本: {version}，文件数: {len(files)}")

if __name__ == "__main__":
    main()