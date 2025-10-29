#!/usr/bin/env python3
import os, sys, hashlib, json, fnmatch, difflib
from pathlib import Path

CFG = Path("knowledge/registry/STRICT.yaml")
try:
    import yaml  # PyYAML
except ImportError:
    print("PyYAML no instalado: pip install pyyaml", file=sys.stderr); sys.exit(2)

def load_cfg():
    with open(CFG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def should_ignore(path, patterns):
    # normalizar con / para comparar
    p = str(path.as_posix())
    for pat in patterns:
        if fnmatch.fnmatch(p, pat):
            return True
    return False

def walk_files(paths, ignore_globs):
    for root in paths:
        root = Path(root)
        if not root.exists(): 
            continue
        for dirpath, _, filenames in os.walk(root):
            dp = Path(dirpath)
            if should_ignore(dp, ignore_globs):
                continue
            for name in filenames:
                fp = dp / name
                if should_ignore(fp, ignore_globs): 
                    continue
                yield fp

def main():
    cfg = load_cfg()
    scan_paths = cfg.get("scan_paths", ["."])
    ignore = cfg.get("ignore_globs", [])
    allow = set(map(str.lower, cfg.get("duplicate_filename_allowlist", [])))
    must_unique = set(map(str.lower, cfg.get("must_be_unique", [])))
    thr = float(cfg.get("near_duplicate_threshold", 0.9))

    files = list(walk_files(scan_paths, ignore))
    by_name = {}
    by_hash = {}
    names = []

    for f in files:
        name = f.name.lower()
        by_name.setdefault(name, []).append(f)
        try:
            h = sha256(f)
            by_hash.setdefault(h, []).append(f)
        except Exception:
            # archivos sin permiso/raros los salteamos
            continue
        names.append((name, f))

    errors = []
    warnings = []

    # 1) Duplicado por nombre
    for name, fs in by_name.items():
        if len(fs) > 1 and name not in allow:
            # Si está en must_be_unique, lo marcamos como error fuerte
            if name in must_unique:
                errors.append({
                    "type": "duplicate_name_strict",
                    "name": name,
                    "files": list(map(str, fs))
                })
            else:
                warnings.append({
                    "type": "duplicate_name",
                    "name": name,
                    "files": list(map(str, fs))
                })

    # 2) Duplicado por contenido (hash)
    for h, fs in by_hash.items():
        if len(fs) > 1:
            warnings.append({
                "type": "duplicate_content",
                "sha256": h,
                "files": list(map(str, fs))
            })

    # 3) Casi duplicados (similaridad de nombres)
    # agrupamos por base name sin extensión para detectar dashboard.py vs dashboard_old.py
    bases = [(Path(p).stem.lower(), p) for _, p in names]
    for i in range(len(bases)):
        for j in range(i+1, len(bases)):
            n1, p1 = bases[i]
            n2, p2 = bases[j]
            if n1 == n2: 
                continue
            sim = difflib.SequenceMatcher(a=n1, b=n2).ratio()
            if sim >= thr:
                warnings.append({
                    "type": "near_duplicate_name",
                    "similarity": round(sim, 3),
                    "a": str(p1),
                    "b": str(p2)
                })

    out = {"errors": errors, "warnings": warnings}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    # Si hay errores fuertes, salimos con 2; si solo warnings, con 1
    if errors:
        sys.exit(2)
    elif warnings:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
