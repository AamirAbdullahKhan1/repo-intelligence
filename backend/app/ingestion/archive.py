"""Validate the entire archive before extracting regular files. Never run target code."""
import re
import stat
import zipfile
from pathlib import Path

MAX_FILES = 5000
MAX_EXPANDED = 100 * 1024 * 1024
MAX_FILE = 12 * 1024 * 1024
MAX_COMPRESSED = 50 * 1024 * 1024
RESERVED = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', re.I)

def extract_archive(archive: Path, destination: Path) -> Path:
    if archive.stat().st_size > MAX_COMPRESSED:
        raise ValueError('Archive exceeds the 50 MiB upload limit')
    try:
        with zipfile.ZipFile(archive) as z:
            members = z.infolist()
            if len(members) > MAX_FILES:
                raise ValueError('Archive exceeds the 5,000 entry limit')
            seen, files, checked, expanded, spellings = set(), set(), [], 0, {}
            for item in members:
                name = item.orig_filename.replace('\\', '/')
                parts = name.rstrip('/').split('/')
                if len(parts)>32 or len(name)>1024 or any(len(p)>255 for p in parts):
                    raise ValueError('Archive path complexity limit exceeded')
                if (not parts or name.startswith('/') or any(
                    p in ('', '.', '..') or ':' in p or p[-1:] in (' ', '.') or
                    RESERVED.match(p) or any(ord(c) < 32 for c in p) or any(c in p for c in '<>"|?*')
                    for p in parts)):
                    raise ValueError('Unsafe archive path')
                mode = item.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError('Archive symlinks and special files are prohibited')
                directory = item.is_dir()
                if kind == stat.S_IFDIR and not directory:
                    raise ValueError('Conflicting archive entry type')
                key = '/'.join(parts).casefold()
                for depth in range(1,len(parts)+1):
                    spelling='/'.join(parts[:depth])
                    previous=spellings.setdefault(spelling.casefold(),spelling)
                    if previous!=spelling:
                        raise ValueError('Case-conflicting archive directory path')
                if key in seen:
                    raise ValueError('Duplicate or case-conflicting archive path')
                seen.add(key)
                if not directory:
                    files.add(key)
                if item.flag_bits & 1:
                    raise ValueError('Encrypted archives are unsupported')
                expanded += item.file_size
                if item.file_size > MAX_FILE or expanded > MAX_EXPANDED:
                    raise ValueError('Archive expanded size limit exceeded')
                if item.file_size > 1024 * 1024 and item.file_size > max(1, item.compress_size) * 200:
                    raise ValueError('Archive compression ratio limit exceeded')
                checked.append((item, parts, directory))
            for key in seen:
                if any('/'.join(key.split('/')[:i]) in files for i in range(1, len(key.split('/')))):
                    raise ValueError('Archive file/directory path conflict')
            destination.mkdir(parents=True, exist_ok=False)
            actual_total = 0
            for item, parts, directory in checked:
                target = destination.joinpath(*parts)
                if not target.resolve().is_relative_to(destination.resolve()):
                    raise ValueError('Unsafe extraction destination')
                if directory:
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                count = 0
                with z.open(item) as source, target.open('xb') as output:
                    while chunk := source.read(65536):
                        count += len(chunk)
                        actual_total += len(chunk)
                        if count > MAX_FILE or actual_total > MAX_EXPANDED:
                            raise ValueError('Archive actual expanded size limit exceeded')
                        output.write(chunk)
                if count != item.file_size:
                    raise ValueError('Archive size mismatch')
    except (zipfile.BadZipFile, NotImplementedError, RuntimeError) as exc:
        raise ValueError('Invalid or unsupported ZIP archive') from exc
    children = list(destination.iterdir())
    return children[0] if len(children) == 1 and children[0].is_dir() else destination
