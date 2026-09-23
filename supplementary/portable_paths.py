"""Portable paths for saved metadata; resolve project paths against ROOT.

Project paths are stored as outputs/... or supplementary/... relative to the
folder containing BKT_experiments.ipynb. External library paths are diagnostic
labels only, so retain their filenames without the machine's user directory.
Runtime file access continues to use the original Path objects.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]


def portable_path(value):
    text = str(value)
    normalized = text.replace(chr(92), "/")
    if not (PureWindowsPath(text).is_absolute() or PurePosixPath(normalized).is_absolute()):
        return text
    root = ROOT.as_posix().rstrip("/") + "/"
    if normalized.casefold().startswith(root.casefold()):
        return normalized[len(root):]
    if normalized.rstrip("/").casefold() == root.rstrip("/").casefold():
        return "."
    # Archived records may refer to the project before its directory was moved.
    parts = PurePosixPath(normalized).parts
    for anchor in ("outputs", "supplementary"):
        if anchor in parts:
            return PurePosixPath(*parts[parts.index(anchor):]).as_posix()
    if parts[-1] == "BKT_experiments.ipynb":
        return parts[-1]
    return parts[-1]
