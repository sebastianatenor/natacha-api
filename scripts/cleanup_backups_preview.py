#!/usr/bin/env python3
import sys, os, json, time
from pathlib import Path
from datetime import datetime, timezone

# Directorios a inspeccionar (mismo criterio que en Cloud Run)
BASE_DIR = Path(".").resolve()
SAFE_DIRS = [BASE_DIR, BASE_DIR / "routes", BASE_DIR / "scripts"]

PATTERNS = (
    ".bak",         # incluye *.bak y *.bak.<timestamp>
    ".backup",
    ".old",
    "~",            # archivos terminados en ~
)

def is_suspect(p: Path) -> bool:
    name = p.name
    if not p.is_file():
        return False
    if name.endswith("~"):
        return True
    if ".bak." in name:
        return True
    for pat in PATTERNS:
        if pat in name:
            return True
    return False

def scan():
    items = []
    for folder in SAFE_DIRS:
        if not folder.exists():
            continue
        for p in folder.rglob("*"):
            if is_suspect(p):
                try:
                    st = p.stat()
                    items.append({
                        "path": str(p.resolve()),
                        "relpath": str(p.resolve().relative_to(BASE_DIR)),
                        "dir": str(p.parent.resolve().relative_to(BASE_DIR)),
                        "size": st.st_size,
                        "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
                    })
                except Exception as e:
                    items.append({"path": str(p), "error": str(e)})
    return items

def human(n: int) -> str:
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.0f} PB"

def main():
    items = scan()
    by_dir = {}
    for it in items:
        d = it.get("dir", ".")
        by_dir.setdefault(d, {"count": 0, "total_size": 0, "samples": []})
        by_dir[d]["count"] += 1
        by_dir[d]["total_size"] += int(it.get("size", 0))
        if len(by_dir[d]["samples"]) < 5:
            by_dir[d]["samples"].append({"relpath": it.get("relpath"), "size": it.get("size")})

    summary = []
    for d, meta in by_dir.items():
        summary.append({
            "dir": d,
            "count": meta["count"],
            "total_size": meta["total_size"],
            "total_size_h": human(meta["total_size"]),
            "samples": meta["samples"],
        })
    summary.sort(key=lambda x: (-x["count"], -x["total_size"]))

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "base": str(BASE_DIR),
        "total_suspects": len(items),
        "directories": summary,
    }

    # Guardar a disco
    ts = time.strftime("%Y%m%d-%H%M%S")
    outdir = Path("backups")
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / f"preview-{ts}.json"
    outfile.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Resumen al stdout
    print(f"✅ Preview generado: {outfile}")
    print(f"Total sospechosos: {report['total_suspects']}")
    top = summary[:10]
    if not top:
        print("(no se encontraron archivos sospechosos)")
        return
    print("\nTop directorios (máx 10):")
    for row in top:
        print(f"- {row['dir']:<40} {row['count']:>4} files  {row['total_size_h']:>8}")

if __name__ == "__main__":
    sys.exit(main())
