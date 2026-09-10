"""Recoverable per-project writes; backups never replace newer user edits."""

import contextlib
import hashlib
import json
import os
import re
import stat
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def safe_path(target: Path, rel: Path) -> Path:
    if not rel.parts or rel.is_absolute() or ".." in rel.parts or rel.parts[0] == ".git":
        raise ValueError(f"Invalid destination path: {rel}")
    cursor = target
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"Refusing symlink in destination: {cursor}")
        if cursor.exists() and cursor != target / rel and not cursor.is_dir():
            raise ValueError(f"Not a directory: {cursor}")
    if cursor.exists() and not cursor.is_file():
        raise ValueError(f"Destination is not a regular file: {cursor}")
    return cursor


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".agent-sync-", delete=False) as f:
            tmp = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        tmp.chmod(mode)
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def fingerprint(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def backup_root(target: Path, custom: Path | None = None) -> Path:
    root = (custom or target.parent / ".agent-system-backups").absolute()
    # Reject symlink components before canonicalization, including a custom root.
    for path in [root, *root.parents]:
        if path.is_symlink():
            raise ValueError(f"Backup root contains a symlink: {path}")
    root = root.resolve()
    if root == target or target in root.parents:
        raise ValueError("Backup root must be outside the target project")
    return root


@contextlib.contextmanager
def project_lock(target: Path, root: Path):
    # Lock identity is independent of a user-selected backup location.
    import fcntl  # Supported sync hosts: macOS and Linux; fail before writes elsewhere.
    lock_dir = backup_root(target) / ".locks"
    if lock_dir.is_symlink():
        raise ValueError("Refusing symlinked lock directory")
    lock_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    name = hashlib.sha256(str(target).encode()).hexdigest() + ".lock"
    lock_path = safe_path(lock_dir, Path(name))
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError(f"Another framework writer is active: {target}") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def save_manifest(backup: Path, manifest: dict) -> None:
    atomic_write(backup / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())


def apply_batch(target: Path, pending: dict[Path, bytes | None], *, root: Path,
                writer=atomic_write, version="unknown", modes=None) -> Path | None:
    """Caller holds project_lock. Validate, backup, apply; undo on caught failure."""
    changes = {}
    for rel, data in pending.items():
        path = safe_path(target, rel)
        original = path.read_bytes() if path.exists() else None
        if original != data:
            changes[rel] = (original, data)
    if not changes:
        return None
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
    backup = root / name
    backup.mkdir(mode=0o700)
    manifest = {"schema_version": 1, "target": str(target), "version": version,
                "status": "prepared", "created_utc": datetime.now(timezone.utc).isoformat(), "files": {}}
    for rel, (old, new) in changes.items():
        path = safe_path(target, rel)
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
        manifest["files"][str(rel)] = {
            "before_sha256": hashlib.sha256(old).hexdigest() if old is not None else None,
            "after_sha256": hashlib.sha256(new).hexdigest() if new is not None else None,
            "before_mode": mode}
        if old is not None:
            stored = safe_path(backup, Path("before") / rel)
            atomic_write(stored, old)
            stored.chmod(0o600)
    save_manifest(backup, manifest)
    attempted = []
    try:
        # Version is last even for reverse/restore operations.
        ordered = sorted(changes, key=lambda rel: rel == Path(".agent-system-version"))
        for rel in ordered:
            path = safe_path(target, rel)
            entry = manifest["files"][str(rel)]
            if fingerprint(path) != entry["before_sha256"]:
                raise ValueError(f"Concurrent file change before write: {rel}")
            attempted.append(rel)
            data = changes[rel][1]
            if data is None:
                path.unlink()
            else:
                writer(path, data)
                if modes and modes.get(rel) is not None:
                    path.chmod(modes[rel])
        manifest["status"] = "applied"
        save_manifest(backup, manifest)
    except BaseException:
        conflicts = []
        for rel in reversed(attempted):
            try:
                path = safe_path(target, rel)
                entry = manifest["files"][str(rel)]
                current = fingerprint(path)
                if current == entry["before_sha256"]:
                    continue
                if current != entry["after_sha256"]:
                    conflicts.append(str(rel))
                    continue
                old = changes[rel][0]
                if old is None:
                    path.unlink()
                else:
                    atomic_write(path, old)
                    path.chmod(entry["before_mode"])
            except (OSError, ValueError):
                conflicts.append(str(rel))
        manifest["status"] = "recovery_required" if conflicts else "rolled_back"
        manifest["recovery_conflicts"] = conflicts
        try:
            save_manifest(backup, manifest)
        finally:
            print(f"Recovery record: {backup}; status: {manifest['status']}")
        raise
    return backup


def restore_plan(target: Path, backup: Path) -> tuple[dict, dict]:
    backup = backup.absolute()
    for part in [backup, *backup.parents]:
        if part.is_symlink():
            raise ValueError("Refusing symlinked recovery record")
    manifest = json.loads(safe_path(backup, Path("manifest.json")).read_text())
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or manifest.get("target") != str(target):
        raise ValueError("Recovery record belongs to another target or schema")
    if not isinstance(manifest.get("files"), dict):
        raise ValueError("Recovery files must be a mapping")
    pending, modes = {}, {}
    for name, entry in manifest["files"].items():
        if not isinstance(entry, dict):
            raise ValueError("Invalid recovery entry")
        rel = Path(name)
        path = safe_path(target, rel)
        for key in ("before_sha256", "after_sha256"):
            if entry[key] is not None and not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                raise ValueError("Invalid recovery hash")
        mode = entry["before_mode"]
        if mode is not None and (type(mode) is not int or not 0 <= mode <= 0o777):
            raise ValueError("Invalid recovery mode")
        data = None
        if entry["before_sha256"] is not None:
            original = safe_path(backup, Path("before") / rel)
            if fingerprint(original) != entry["before_sha256"]:
                raise ValueError(f"Backup content changed: {rel}")
            data = original.read_bytes()
        current = fingerprint(path)
        if current not in (entry["before_sha256"], entry["after_sha256"]):
            raise ValueError(f"Newer local edit prevents restore: {rel}")
        pending[rel], modes[rel] = data, mode
    return pending, modes
