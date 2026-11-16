"""Compare the prepared Windows distribution against remote commit e19cd1af (Fase 0)."""
import hashlib
import json
from pathlib import Path

# docs/production/evidence/<this file> -> repository root
BASE = Path(__file__).resolve().parents[3]
CLONE = Path(__file__).parent / "remote_probe"
SKIP = {"__pycache__", ".pytest_cache", ".git"}


def inventory(root):
    out = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if SKIP & set(path.relative_to(root).parts):
            continue
        out[path.relative_to(root).as_posix()] = path.read_bytes()
    return out


def lf(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def raw(data):
    return hashlib.sha256(data).hexdigest()


base, clone = inventory(BASE), inventory(CLONE)
only_base = sorted(set(base) - set(clone))
only_clone = sorted(set(clone) - set(base))
raw_diff, lf_diff = [], []
for name in sorted(set(base) & set(clone)):
    if raw(base[name]) != raw(clone[name]):
        raw_diff.append(name)
        if lf(base[name]) != lf(clone[name]):
            lf_diff.append(name)

print(json.dumps({
    "commit": "e19cd1af045ea22e4518f3795f9c5070979a924f",
    "files_distribution": len(base),
    "files_commit": len(clone),
    "only_in_distribution": only_base,
    "only_in_commit": only_clone,
    "differ_raw_bytes": raw_diff,
    "differ_after_lf_normalisation": lf_diff,
}, indent=2))
