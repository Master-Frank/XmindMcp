"""Filesystem listing adapter, separate from document processing."""
import fnmatch
import os
from pathlib import Path


def list_files(directory: Path, recursive=True, pattern=None, max_depth=None):
    results = []
    for root, dirs, files in os.walk(directory):
        relative = Path(root).relative_to(directory)
        depth = len(relative.parts)
        if not recursive or (max_depth is not None and depth >= max_depth):
            dirs[:] = []
        for name in files:
            if not name.endswith('.xmind') or (pattern and not fnmatch.fnmatch(name, pattern)):
                continue
            path = Path(root) / name
            stat = path.stat()
            results.append({"name": name, "path": str(path), "relative_path": str(path.relative_to(directory)),
                            "size": stat.st_size, "modified": stat.st_mtime})
    return results
