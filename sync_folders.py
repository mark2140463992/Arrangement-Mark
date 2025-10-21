#!/usr/bin/env python3
import os, json, argparse, re
from typing import Union, Dict, List

CONFIG = "taxonomy.json"

# ---------- 基础IO ----------
def load_config(path=CONFIG) -> Union[Dict, List]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg, path=CONFIG):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"💾 Updated {path}")

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    keep = os.path.join(path, ".keep")
    if not os.path.exists(keep):
        open(keep, "w").close()

# ---------- 同步创建目录 ----------
def sync_node(base: str, node: Union[Dict, List, str]):
    if isinstance(node, dict):
        for name, child in node.items():
            next_base = os.path.join(base, name)
            ensure_dir(next_base)
            sync_node(next_base, child)
    elif isinstance(node, list):
        for name in node:
            ensure_dir(os.path.join(base, name))
    elif isinstance(node, str):
        ensure_dir(os.path.join(base, node))
    else:
        raise TypeError(f"Unsupported node type: {type(node)}")

def sync_from_config(root="."):
    cfg = load_config()
    sync_node(root, cfg)
    print("✅ 所有目录已创建完成，并添加 .keep 文件。")

# ---------- 在配置里插入新路径 ----------
def _ensure_branch(obj: Union[Dict, List], parts: List[str]):
    if not parts:
        return obj
    head, *tail = parts

    if isinstance(obj, list):
        if tail:  # 想在list下继续分层：把list“升级”为dict
            promoted = {name: [] for name in obj}
            obj.clear(); obj.extend(["__PROMOTED__"])
            obj = {"__PROMOTED_DICT__": promoted}
            return _ensure_branch(obj, [head] + tail)
        else:
            if head not in obj and "__PROMOTED__" not in obj:
                obj.append(head)
            return obj

    if isinstance(obj, dict):
        if "__PROMOTED_DICT__" in obj:
            obj = obj["__PROMOTED_DICT__"]
        if head not in obj:
            obj[head] = [] if not tail else {}
        obj[head] = _ensure_branch(obj[head], tail)
        return obj

    raise TypeError("Invalid config structure while adding path.")

def add_path_to_config(path_str: str):
    parts = [p for p in path_str.split("/") if p]
    cfg = load_config()
    new_cfg = _ensure_branch(cfg, parts)
    if isinstance(new_cfg, dict) and "__PROMOTED_DICT__" in new_cfg:
        new_cfg = new_cfg["__PROMOTED_DICT__"]
    save_config(new_cfg)
    sync_from_config(".")

# ---------- 从文件名推断风格（可选） ----------
STYLE_PATTERNS = [
    re.compile(r"\[(?P<path>[^\]]+)\]"),  # 例：[J-Pop>J-Rock]
    re.compile(r"style\s*[:=]\s*(?P<path>[A-Za-z0-9_\-\s>]+)", re.IGNORECASE),  # 例：style=KawaiiBass
]

def infer_paths_from_filename(name: str) -> List[str]:
    results = []
    for pat in STYLE_PATTERNS:
        m = pat.search(name)
        if not m:
            continue
        raw = m.group("path").strip()
        parts = [p.strip().replace(" ", "") for p in raw.split(">") if p.strip()]
        if parts:
            results.append("/".join(parts))
    return results

def infer_and_update(scan_dir: str):
    discovered = set()
    for root, _, files in os.walk(scan_dir):
        for fn in files:
            for p in infer_paths_from_filename(fn):
                discovered.add(p)
    if not discovered:
        print("🔎 没发现风格标签。示例：[J-Pop>J-Rock] 或 style=KawaiiBass")
        return
    print("🧭 将新增这些路径：")
    for p in sorted(discovered):
        print("  •", p)
        add_path_to_config(p)

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Sync & grow your folder taxonomy.")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("sync", help="根据 taxonomy.json 创建/补全目录")

    p_add = sub.add_parser("add", help="添加新分支并创建目录")
    p_add.add_argument("path", help='如 "J-Pop/J-Rock" 或 "Pop/Rhythm/UKGarage"')

    p_infer = sub.add_parser("infer", help="从文件名推断风格并新增目录")
    p_infer.add_argument("--scan", default=".", help="扫描路径（默认当前目录）")

    args = parser.parse_args()
    if args.cmd == "add":
        add_path_to_config(args.path)
    elif args.cmd == "infer":
        infer_and_update(args.scan)
    else:
        sync_from_config(".")

if __name__ == "__main__":
    main()
