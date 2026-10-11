"""Preflight and rollback explicit runtime upgrades (not crash-atomic installs).

Only bundle files and the install manifest are written. Compatibility runs on
an isolated staged bundle before writes. A cooperating upgrader lock prevents
concurrent upgrades; arbitrary external writers and power loss are out of scope.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, Iterable

MANIFEST = ".gstack/runtime-install.json"
LOCK = ".gstack/runtime-upgrade.lock"


def _path(root: Path, relative: str) -> Path:
    part = PurePosixPath(relative)
    if not relative or relative != part.as_posix() or part.is_absolute() or ".." in part.parts or "\\" in relative:
        raise ValueError(f"unsafe bundle path: {relative}")
    path = root / relative
    for ancestor in (path, *path.parents):
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise ValueError(f"symlink in bundle path: {relative}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"bundle path escapes repository: {relative}")
    if path.exists() and not path.is_file():
        raise ValueError(f"bundle path is not a file: {relative}")
    return path


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes, mode: int) -> None:
    """Replace one file atomically; transaction rollback handles earlier files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".runtime-upgrade-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def check_compatibility(stage: Path, files: list[str]) -> None:
    """Compile every Python file and load the framework's main CLI graphs.

    This is a runtime interface smoke, not business acceptance or an exhaustive
    compatibility guarantee. Additional target checks can be supplied by callers.
    """
    for relative in files:
        if relative.endswith(".py"):
            compile((stage / relative).read_bytes(), relative, "exec")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("KK_") and key not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = []
    if ".gstack/scripts/adapter_runtime.py" in files:
        commands.append([sys.executable, "-c",
                         "import sys; from pathlib import Path; "
                         "sys.path.insert(0, str(Path.cwd()/'.gstack/scripts')); "
                         "from adapter_runtime import load_adapter_runtime; "
                         "[load_adapter_runtime(Path.cwd(), p.parent.name) "
                         "for p in Path('adapters').glob('*/runtime.json')]"])
    for relative in (".gstack/scripts/gstack_loop.py", ".gstack/scripts/qa_verify.py"):
        if relative not in files:
            continue
        commands.append([sys.executable, str(stage / relative), "--help"])
    for command in commands:
        completed = subprocess.run(command,
                                   cwd=stage, env=env, capture_output=True,
                                   text=True, timeout=30)
        if completed.returncode:
            raise RuntimeError(f"runtime compatibility failed: {command[1]}: "
                               f"{completed.stderr[-1500:]}")


def upgrade_runtime_bundle(*, source_root: Path, target_root: Path,
                           files: Iterable[str], dry_run: bool,
                           release_version: str,
                           compatibility_check: Callable[[Path], object] | None = None) -> dict:
    """Upgrade the entire known bundle or leave its previous contents intact.

    Existing differing files require their exact previous install hash. Invalid
    manifests, missing source files, symlinks and customizations block all writes.
    A callback runs after built-in checks and must raise or return False to fail.
    """
    source_root, target_root = Path(source_root).resolve(), Path(target_root).resolve()
    paths = list(dict.fromkeys(files))
    result = dict(created=False, ok=False, dry_run=dry_run, created_paths=[],
                  would_create=[], preserved_paths=[], source_missing=[],
                  preserved_differences=[], updated_paths=[], upgrade_complete=False,
                  upgrade_status="blocked", release_version=release_version,
                  message="", errors=[])
    lock_path = target_root / LOCK
    locked = False
    created_directories: list[Path] = []
    snapshots: dict[str, tuple[bytes, int] | None] = {}
    attempted: list[str] = []

    def fail(status: str, error: object) -> dict:
        result.update(upgrade_status=status, message=str(error))
        result["errors"].append(str(error))
        return result

    try:
        if not paths or MANIFEST in paths or LOCK in paths:
            return fail("blocked", "runtime bundle is empty or contains reserved paths")
        manifest_path = _path(target_root, MANIFEST)
        _path(target_root, LOCK)
        if not dry_run:
            if not target_root.is_dir():
                return fail("blocked", "upgrade target must be an existing repository")
            if not lock_path.parent.exists():
                lock_path.parent.mkdir()
                created_directories.append(lock_path.parent)
            try:
                descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                return fail("locked", "runtime upgrade already active; inspect stale lock before retry")
            os.close(descriptor)
            locked = True
        if manifest_path.exists():
            baseline = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(baseline, dict) or not isinstance(baseline.get("files"), dict):
                return fail("blocked", "invalid runtime install manifest")
            hashes = baseline["files"]
        else:
            hashes = {}
        incoming: dict[str, tuple[bytes, int]] = {}
        for relative in paths:
            source, target = _path(source_root, relative), _path(target_root, relative)
            if not source.exists():
                result["source_missing"].append(relative)
                continue
            data = source.read_bytes()
            incoming[relative] = (data, source.stat().st_mode & 0o777)
            old = (target.read_bytes(), target.stat().st_mode & 0o777) if target.exists() else None
            snapshots[relative] = old
            if old is not None:
                result["preserved_paths"].append(relative)
                if old[0] != data and _digest(old[0]) != hashes.get(relative):
                    result["preserved_differences"].append(dict(
                        path=relative, source_sha256=_digest(data),
                        target_sha256=_digest(old[0]), action="review-before-upgrade"))
            if old is None or old[0] != data:
                result["would_create"].append(relative)
        if result["source_missing"] or result["preserved_differences"]:
            status = "missing-source" if result["source_missing"] else "conflicts-preserved"
            return fail(status, "whole runtime upgrade blocked; no bundle files or manifest changed")
        snapshots[MANIFEST] = ((manifest_path.read_bytes(), manifest_path.stat().st_mode & 0o777)
                               if manifest_path.exists() else None)
        with tempfile.TemporaryDirectory(prefix="kk-runtime-upgrade-") as temporary:
            stage = Path(temporary)
            # Preserve target configuration in the isolated runtime smoke.
            for folder in ("adapters", ".gstack/workflows"):
                location = target_root / folder
                if location.is_symlink() or location.parent.is_symlink():
                    raise ValueError(f"symlink in compatibility configuration: {folder}")
                if location.exists():
                    for item in location.rglob("*"):
                        if item.is_symlink():
                            raise ValueError(f"symlink in compatibility configuration: {item.relative_to(target_root)}")
                    shutil.copytree(location, stage / folder)
            for relative, (data, mode) in incoming.items():
                _write(stage / relative, data, mode)
            try:
                check_compatibility(stage, paths)
                if compatibility_check and compatibility_check(stage) is False:
                    raise RuntimeError("target compatibility check returned False")
            except Exception as error:
                return fail("verification-failed", error)
        if dry_run:
            result.update(ok=True, upgrade_status="dry-run", message="preflight and staged compatibility passed; no files written")
            return result
        # Recheck all snapshots to avoid silently replacing an intervening edit.
        for relative, old in snapshots.items():
            target = _path(target_root, relative)
            current = (target.read_bytes(), target.stat().st_mode & 0o777) if target.exists() else None
            if current != old:
                return fail("conflicts-preserved", f"file changed during preflight: {relative}")
        next_hashes = dict(hashes)
        for relative, (data, mode) in incoming.items():
            next_hashes[relative] = _digest(data)
            if relative not in result["would_create"]:
                continue
            target = _path(target_root, relative)
            missing = []
            parent = target.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            created_directories.extend(reversed(missing))
            attempted.append(relative)
            _write(target, data, mode)
            result["created_paths" if snapshots[relative] is None else "updated_paths"].append(relative)
        manifest = (json.dumps(dict(release_version=release_version, files=next_hashes), indent=2) + "\n").encode()
        attempted.append(MANIFEST)
        _write(manifest_path, manifest, 0o644)
        result.update(created=bool(result["created_paths"]), ok=True, upgrade_complete=True,
                      upgrade_status="complete", message="whole runtime bundle upgraded after staged compatibility checks")
        return result
    except Exception as error:
        rollback_errors = []
        for relative in reversed(attempted):
            try:
                target = _path(target_root, relative)
                old = snapshots[relative]
                if old is None:
                    target.unlink(missing_ok=True)
                else:
                    # Rollback bypasses the writer so an injected write failure
                    # cannot also prevent restoring the original bytes.
                    target.write_bytes(old[0])
                    target.chmod(old[1])
            except Exception as rollback_error:
                rollback_errors.append(f"{relative}: {rollback_error}")
        result["created_paths"], result["updated_paths"] = [], []
        result["rollback_errors"] = rollback_errors
        return fail("rollback-failed" if rollback_errors else ("rolled-back" if attempted else "blocked"), error)
    finally:
        if locked:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError as error:
                result.setdefault("warnings", []).append(f"upgrade lock could not be removed: {error}")
        if not result["ok"]:
            for directory in reversed(created_directories):
                try:
                    directory.rmdir()
                except OSError:
                    pass
