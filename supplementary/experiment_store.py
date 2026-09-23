"""Lossless experiment archives with temporary compatibility workspaces.

The original logical filenames are retained inside four ZIP files. Existing
numerical code runs against those filenames while managed_outputs is active.
Every member is SHA-256 verified before any loose copy is removed. Failed runs
are archived too; a failed archive operation leaves the loose data untouched.
"""
from __future__ import annotations

import argparse
import atexit
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
STORE = OUTPUTS / "data"
GROUPS = ("ou", "double_well", "alanine", "shared")
MANIFEST = "_manifest.json"
CATALOG = STORE / "catalog.json"
_notebook_context = None


def group_for(logical):
    parts = PurePosixPath(str(logical).replace("\\", "/")).parts
    if len(parts) < 2 or parts[0] != "outputs":
        return None
    name = parts[1]
    if name in {"data", "figures", "all_experiment_results_and_assessment.md", "revision_results.json"}:
        return None
    if name == "alanine":
        return "alanine"
    if name.startswith("ou_"):
        return "ou"
    if len(parts) > 3 and parts[1:3] == ("cache", "numerics"):
        if parts[3].startswith("ou_"):
            return "ou"
        if parts[3] == "reference_statistics":
            return "shared"
    if name in {"cache", "admissible_source", "data_comparison", "revision", "tables"} or name.startswith("product_"):
        return "double_well"
    if len(parts) == 2 and name.endswith((".json", ".txt", ".csv", ".log", ".npz")):
        return "shared"
    return None


def checked_path(logical):
    name = PurePosixPath(logical)
    if name.is_absolute() or ".." in name.parts or "\\" in logical or ":" in logical:
        raise ValueError(f"Unsafe archive member: {logical}")
    path = (ROOT / Path(*name.parts)).resolve()
    if not path.is_relative_to(OUTPUTS.resolve()) or group_for(logical) is None:
        raise ValueError(f"Archive member is outside the data area: {logical}")
    return path


def digest(stream):
    h = hashlib.sha256()
    size = 0
    while block := stream.read(1024 * 1024):
        h.update(block)
        size += len(block)
    return {"sha256": h.hexdigest(), "bytes": size}


def file_digest(path):
    with path.open("rb") as stream:
        return digest(stream)


def manifest(group):
    path = STORE / f"{group}.zip"
    if not path.exists():
        return {}
    with zipfile.ZipFile(path) as archive:
        record = json.loads(archive.read(MANIFEST))
        if record["group"] != group:
            raise ValueError("Archive group mismatch")
        return record["members"]


def verify_archive(path, group):
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read(MANIFEST))
        expected = data["members"]
        names = archive.namelist()
        if data["group"] != group or len(set(names)) != len(names) or set(names) != set(expected) | {MANIFEST}:
            raise ValueError(f"Invalid archive inventory: {path}")
        for logical, record in expected.items():
            checked_path(logical)
            if group_for(logical) != group:
                raise ValueError(f"Incorrect experiment classification: {logical}")
            with archive.open(logical) as stream:
                if digest(stream) != record:
                    raise ValueError(f"Archive checksum mismatch: {logical}")
    return expected


def loose_files(group):
    return {p.relative_to(ROOT).as_posix(): p for p in OUTPUTS.rglob("*")
            if p.is_file() and group_for(p.relative_to(ROOT).as_posix()) == group
            and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def update_catalog():
    members, groups = {}, {}
    for group in GROUPS:
        rows = manifest(group)
        if not rows:
            continue
        members.update({name: {"group": group, **record} for name, record in rows.items()})
        groups[group] = {"archive": f"{group}.zip", "files": len(rows),
                         "original_bytes": sum(row["bytes"] for row in rows.values()),
                         "archive_bytes": (STORE / f"{group}.zip").stat().st_size}
    data = {"format": 1, "description": "Lossless archives; member paths are original workspace-relative paths.",
            "groups": groups, "members": dict(sorted(members.items()))}
    temporary = CATALOG.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    return data


def pack_group(group):
    """Commit and verify a replacement archive before removing any loose file."""
    STORE.mkdir(parents=True, exist_ok=True)
    existing = manifest(group)
    loose = loose_files(group)
    scanned = {logical: file_digest(path) for logical, path in loose.items()}
    records = {**existing, **scanned}
    for logical in list(records):
        destination_group = group_for(logical)
        if destination_group != group:
            # Reclassification is allowed only after the new archive is verified.
            destination = verify_archive(STORE / f"{destination_group}.zip", destination_group)
            if destination.get(logical) != records[logical]:
                raise RuntimeError(f"Reclassified member has no identical archived copy: {logical}")
            del records[logical]
    if not records:
        return
    target = STORE / f"{group}.zip"
    changed = records != existing or not target.exists()
    if changed:
        temporary = target.with_suffix(".zip.pending")
        old = zipfile.ZipFile(target) if target.exists() else None
        try:
            with zipfile.ZipFile(temporary, "w", allowZip64=True) as archive:
                for logical in sorted(records):
                    checked_path(logical)
                    info = zipfile.ZipInfo(logical)
                    info.compress_type = zipfile.ZIP_STORED if logical.endswith(".npz") else zipfile.ZIP_DEFLATED
                    source = loose[logical].open("rb") if logical in loose else old.open(logical)
                    with source, archive.open(info, "w", force_zip64=True) as destination:
                        shutil.copyfileobj(source, destination, length=1024 * 1024)
                archive.writestr(MANIFEST, json.dumps({"format": 1, "group": group, "members": records}, indent=2),
                                 compress_type=zipfile.ZIP_DEFLATED)
            verify_archive(temporary, group)
            # Detect concurrent writes before committing or deleting anything.
            if any(file_digest(path) != scanned[logical] for logical, path in loose.items()):
                raise RuntimeError("Loose data changed while packing; originals were retained")
            if old is not None:
                old.close()
                old = None
            temporary.replace(target)
        finally:
            if old is not None:
                old.close()
    else:
        verify_archive(target, group)
    update_catalog()
    # Each deletion is a checked file with a verified byte-identical archive copy.
    for logical, path in loose.items():
        if path != checked_path(logical) or file_digest(path) != records[logical]:
            raise RuntimeError(f"Refusing to remove a changed loose copy: {logical}")
        path.unlink()
    for directory in sorted({parent for path in loose.values() for parent in path.parents
                             if parent != OUTPUTS and parent.is_relative_to(OUTPUTS)},
                            key=lambda p: len(p.parts), reverse=True):
        if directory.exists() and directory.is_relative_to(OUTPUTS.resolve()) and not any(directory.iterdir()):
            directory.rmdir()


def unpack_group(group):
    archive_path = STORE / f"{group}.zip"
    if not archive_path.exists():
        return
    records = manifest(group)
    with zipfile.ZipFile(archive_path) as archive:
        for logical, record in records.items():
            target = checked_path(logical)
            if target.exists():
                # A user's loose working copy takes precedence and will be saved.
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".extracting")
            with archive.open(logical) as source, temporary.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            if file_digest(temporary) != record:
                raise ValueError(f"Extracted checksum mismatch: {logical}")
            temporary.replace(target)


@contextmanager
def store_lock():
    STORE.mkdir(parents=True, exist_ok=True)
    path = STORE / "session.lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError("Experiment data are already open in another session. Close that session before opening another.") from None
    with os.fdopen(descriptor, "w") as stream:
        stream.write(str(os.getpid()))
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


@contextmanager
def managed_outputs(*groups):
    """Temporarily restore original paths and save all output changes on exit."""
    groups = tuple(dict.fromkeys((*groups, "shared")))
    if any(group not in GROUPS for group in groups):
        raise ValueError(f"Unknown experiment group: {groups}")
    inherited = os.environ.get("BKT_ACTIVE_EXPERIMENT_STORE")
    if inherited:
        state = json.loads(inherited)
        if state["store"] == str(STORE) and (STORE / "session.lock").exists():
            if not set(groups) <= set(state["groups"]):
                raise RuntimeError("The active experiment session does not contain the requested groups")
            yield
            return
    if not CATALOG.exists():
        yield
        return
    with store_lock():
        for group in groups:
            unpack_group(group)
        os.environ["BKT_ACTIVE_EXPERIMENT_STORE"] = json.dumps({"store": str(STORE), "groups": groups})
        try:
            yield
        finally:
            # Archive even an interrupted/failed run, preserving its diagnostics.
            try:
                for group in groups:
                    pack_group(group)
            finally:
                if inherited is None:
                    os.environ.pop("BKT_ACTIVE_EXPERIMENT_STORE", None)
                else:
                    os.environ["BKT_ACTIVE_EXPERIMENT_STORE"] = inherited


def activate_notebook_store():
    """Keep all data available for a notebook kernel; close explicitly or at exit."""
    global _notebook_context
    if _notebook_context is None and CATALOG.exists():
        context = managed_outputs(*GROUPS)
        context.__enter__()
        _notebook_context = context
        atexit.register(close_notebook_store)


def close_notebook_store():
    global _notebook_context
    if _notebook_context is not None:
        context, _notebook_context = _notebook_context, None
        context.__exit__(None, None, None)


def archive_links(markdown, report_path):
    """Link archived results to their experiment ZIP instead of missing paths."""
    if not CATALOG.exists():
        return markdown
    members = json.loads(CATALOG.read_text(encoding="utf-8"))["members"]
    base = Path(report_path).resolve().parent
    def replace(match):
        target = match.group(1)
        if target.startswith(("#", "http:", "https:", "mailto:")):
            return match.group(0)
        path = (base / target.split("#")[0]).resolve()
        if not path.is_relative_to(ROOT):
            return match.group(0)
        logical = path.relative_to(ROOT).as_posix()
        if logical in members:
            group = members[logical]["group"]
        elif path.exists() and group_for(logical) in GROUPS:
            # New results in an open session are archived when its writer exits.
            group = group_for(logical)
        else:
            contained = {record["group"] for name, record in members.items()
                         if name.startswith(logical.rstrip("/") + "/")}
            if len(contained) != 1:
                return match.group(0)
            group = contained.pop()
        archive = STORE / (group + ".zip")
        relative = Path(os.path.relpath(archive, base)).as_posix()
        return "](" + relative + ")"
    return re.sub(r"\]\(([^\s)]+)\)", replace, markdown)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("pack", "unpack", "verify", "list"):
        part = sub.add_parser(command)
        part.add_argument("groups", nargs="*", metavar="GROUP")
    part = sub.add_parser("read")
    part.add_argument("member")
    part.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "read":
        logical = args.member.replace("\\", "/")
        checked_path(logical)
        group = group_for(logical)
        with zipfile.ZipFile(STORE / f"{group}.zip") as archive:
            if args.output:
                destination = args.output.resolve()
                if destination.is_relative_to(STORE.resolve()):
                    raise ValueError("Do not overwrite a data archive with an extracted member")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(logical) as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
            elif logical.endswith((".json", ".txt", ".csv", ".log", ".py", ".diff")):
                sys.stdout.buffer.write(archive.read(logical))
            else:
                raise ValueError("Use --output for binary members")
        return
    groups = args.groups or GROUPS
    if any(group not in GROUPS for group in groups):
        parser.error("GROUP must be one of: " + ", ".join(GROUPS))
    if args.command == "list":
        for group in groups:
            for name, record in sorted(manifest(group).items()):
                print(f"{group}\t{record['bytes']}\t{name}")
        return
    with store_lock():
        for group in groups:
            if args.command == "pack":
                pack_group(group)
            elif args.command == "unpack":
                unpack_group(group)
            else:
                verify_archive(STORE / f"{group}.zip", group)
            print(f"{args.command}: {group}", flush=True)
        if args.command == "pack":
            print(json.dumps(update_catalog()["groups"], indent=2))


if __name__ == "__main__":
    main()
