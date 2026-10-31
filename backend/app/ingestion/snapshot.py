"""Make source files read-only and check every byte again after analysis."""
import hashlib
import os
import stat
from pathlib import Path

def fingerprint(root: Path) -> dict[str, str]:
    values = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('Snapshot contains a symlink')
        if p.is_file():
            values[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return values

def freeze(root: Path) -> dict[str, str]:
    identity = fingerprint(root)
    for name in identity:
        os.chmod(root / name, stat.S_IREAD)
    return identity

def cleanup_error(function, path, exc):
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    function(path)
