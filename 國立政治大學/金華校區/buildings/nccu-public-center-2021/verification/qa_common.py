"""Shared original-binary-STL I/O. Never repairs, welds, rounds or drops faces."""
from pathlib import Path
import gzip
import hashlib
import json
import struct
import numpy as np


class QAError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise QAError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_stl(path):
    path = Path(path)
    raw = path.read_bytes()
    require(len(raw) >= 84, "Binary STL is shorter than its 84-byte header")
    count = struct.unpack_from('<I', raw, 80)[0]
    require(count > 0, "Binary STL contains no triangles")
    require(len(raw) == 84 + 50 * count,
            f"Binary STL length mismatch: {len(raw)} bytes for {count} triangles")
    dtype = np.dtype([('normal', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')])
    records = np.frombuffer(raw, dtype=dtype, count=count, offset=84)
    triangles = records['v'].astype(np.float64)
    normals = records['normal'].astype(np.float64)
    require(np.isfinite(triangles).all() and np.isfinite(normals).all(),
            "Original STL contains a NaN or infinity")
    return raw, triangles, normals, records['a'].copy()


def write_json(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')


def write_gzip_json(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as handle:
        with gzip.GzipFile(filename='', fileobj=handle, mode='wb', mtime=0) as compressed:
            compressed.write(json.dumps(report, separators=(',', ':'), allow_nan=False).encode())


def checker_inventory():
    root = Path(__file__).resolve().parent
    return {p.name: sha256(p) for p in sorted(root.iterdir())
            if p.suffix in ('.py', '.cpp') and p.is_file()}


def error_report(path, checker, stl, error):
    report = {'passed': False, 'strict_passed': False, 'checker': checker,
              'checks': {'completed_without_error': False},
              'error_type': type(error).__name__, 'error': str(error),
              'stl_sha256': sha256(stl) if Path(stl).is_file() else None,
              'checker_sources_sha256': checker_inventory()}
    write_json(path, report)
    return report


def polygons(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == 'Polygon':
        return [geometry]
    if geometry.geom_type == 'MultiPolygon':
        return list(geometry.geoms)
    raise QAError(f"Unexpected section geometry: {geometry.geom_type}")
