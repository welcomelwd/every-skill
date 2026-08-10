#!/usr/bin/env python3
"""Import bounded, license-preserving source snapshots from public GitHub repos.

The script deliberately never installs dependencies or executes imported code.
It is run by GitHub Actions after the ChatGPT collection task writes a JSON
manifest under knowledge/github-trending/.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "knowledge" / "github-trending"
MAX_PROJECT_BYTES = int(os.environ.get("MAX_PROJECT_BYTES", 25 * 1024 * 1024))
MAX_FILE_BYTES = int(os.environ.get("MAX_FILE_BYTES", 2 * 1024 * 1024))

ALLOWED_CATEGORIES = {"skill", "mcp", "agent", "knowledge"}
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".cache",
    "dist",
    "build",
    "coverage",
    "target",
    "site-packages",
}
SKIP_SUFFIXES = {
    ".7z",
    ".a",
    ".bin",
    ".ckpt",
    ".db",
    ".dmg",
    ".dll",
    ".exe",
    ".gguf",
    ".gz",
    ".iso",
    ".jar",
    ".jpeg",
    ".jpg",
    ".lockb",
    ".mp3",
    ".mp4",
    ".onnx",
    ".p12",
    ".pth",
    ".pyc",
    ".rar",
    ".safetensors",
    ".so",
    ".tar",
    ".tgz",
    ".tif",
    ".tiff",
    ".wav",
    ".webm",
    ".whl",
    ".zip",
}
IMPORTANT_PREFIXES = ("readme", "license", "copying", "notice")
SENSITIVE_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
}


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def component(value: str, field: str) -> str:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", normalized):
        raise ValueError(f"{field} is not a safe path component: {value!r}")
    return normalized


def source_url(project: dict) -> str:
    repository = str(project.get("repository", "")).strip()
    url = str(project.get("source_url", "")).strip()
    if not url and repository:
        url = f"https://github.com/{repository}"
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?", url):
        raise ValueError(f"only public github.com repositories are supported: {url!r}")
    return url.rstrip("/")


def repository_name(project: dict) -> str:
    repository = str(project.get("repository", "")).strip()
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        return repository
    match = re.fullmatch(
        r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:\.git)?/?",
        str(project.get("source_url", "")).strip(),
    )
    if not match:
        raise ValueError(f"invalid repository: {repository!r}")
    return match.group(1)


def project_target(project: dict) -> Path:
    category = component(str(project.get("category", "")), "category")
    subcategory = component(str(project.get("subcategory", "")), "subcategory")
    slug = component(str(project.get("slug", "")), "slug")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"unsupported category: {category}")
    return ROOT / category / subcategory / slug


def load_manifests() -> tuple[list[tuple[Path, dict]], list[str]]:
    manifests: list[tuple[Path, dict]] = []
    errors: list[str] = []
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON ({exc})")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
            continue
        manifests.append((path, data))
    return manifests, errors


def existing_metadata(target: Path) -> dict | None:
    marker = target / "IMPORT-METADATA.json"
    if not marker.is_file():
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def should_skip_file(path: Path, size: int) -> str | None:
    name = path.name.lower()
    if name in SENSITIVE_NAMES or name.startswith(".env"):
        return "sensitive filename"
    if path.suffix.lower() in SKIP_SUFFIXES:
        return "binary, archive, media, or generated artifact"
    if size > MAX_FILE_BYTES and not name.startswith(IMPORTANT_PREFIXES):
        return f"file exceeds {MAX_FILE_BYTES} bytes"
    try:
        with path.open("rb") as handle:
            if b"\0" in handle.read(8192):
                return "binary content"
    except OSError as exc:
        return f"unreadable ({exc})"
    return None


def copy_source(source: Path, destination: Path) -> tuple[int, int, list[str]]:
    total_bytes = 0
    copied_files = 0
    skipped: list[str] = []
    destination.mkdir(parents=True, exist_ok=True)

    for current, directories, files in os.walk(source):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in SKIP_DIRS
            and not (current_path / directory).is_symlink()
        )
        for filename in sorted(files):
            source_file = current_path / filename
            relative = source_file.relative_to(source)
            if source_file.is_symlink():
                skipped.append(f"{relative}: symlink")
                continue
            try:
                size = source_file.stat().st_size
            except OSError as exc:
                skipped.append(f"{relative}: stat failed ({exc})")
                continue
            reason = should_skip_file(source_file, size)
            if reason:
                skipped.append(f"{relative}: {reason}")
                continue
            if total_bytes + size > MAX_PROJECT_BYTES:
                skipped.append(f"{relative}: project exceeds {MAX_PROJECT_BYTES} bytes")
                continue
            target_file = destination / relative
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            total_bytes += size
            copied_files += 1

    return copied_files, total_bytes, skipped


def import_project(project: dict, manifest: Path, imported_at: str) -> tuple[str, str, bool]:
    target = project_target(project)
    repository = repository_name(project)
    url = source_url(project)
    requested_commit = str(project.get("commit", "")).strip() or None
    metadata = existing_metadata(target) if target.exists() else None

    if metadata and requested_commit and metadata.get("resolved_commit") == requested_commit:
        return "up-to-date", f"{target.relative_to(ROOT)} @ {requested_commit}", False

    with tempfile.TemporaryDirectory(prefix="every-skill-import-") as temp_dir:
        temp_root = Path(temp_dir)
        checkout = temp_root / "checkout"
        clone_command = ["git", "clone", "--depth", "1", "--no-tags"]
        requested_ref = str(project.get("ref", "")).strip()
        if requested_ref:
            clone_command.extend(["--branch", requested_ref])
        clone_command.extend([url, str(checkout)])
        run(clone_command)
        resolved_commit = run(["git", "rev-parse", "HEAD"], cwd=checkout)

        if metadata and metadata.get("resolved_commit") == resolved_commit:
            return "up-to-date", f"{target.relative_to(ROOT)} @ {resolved_commit}", False

        staging = temp_root / "snapshot"
        copied_files, total_bytes, skipped = copy_source(checkout, staging)
        if copied_files == 0:
            raise RuntimeError(f"no safe source files remained after filtering for {repository}")

        import_metadata = {
            "schema_version": 1,
            "repository": repository,
            "source_url": url,
            "ref": requested_ref or "default branch",
            "resolved_commit": resolved_commit,
            "category": target.relative_to(ROOT).parts[0],
            "subcategory": target.relative_to(ROOT).parts[1],
            "slug": target.relative_to(ROOT).parts[2],
            "license": project.get("license"),
            "source_date": project.get("source_date"),
            "imported_at": imported_at,
            "download_mode": "bounded source snapshot",
            "copied_files": copied_files,
            "copied_bytes": total_bytes,
            "excluded_files": skipped,
            "execution": "never run by this importer",
        }
        (staging / "IMPORT-METADATA.json").write_text(
            json.dumps(import_metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        if target.exists() and not (target / "IMPORT-METADATA.json").is_file():
            raise RuntimeError(
                f"refusing to overwrite unmanaged directory: {target.relative_to(ROOT)}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        backup = target.parent / f".{target.name}.previous-import"
        if backup.exists():
            shutil.rmtree(backup)
        if target.exists():
            target.rename(backup)
        try:
            shutil.move(str(staging), str(target))
        except Exception:
            if target.exists():
                shutil.rmtree(target)
            if backup.exists():
                backup.rename(target)
            raise
        if backup.exists():
            shutil.rmtree(backup)

    action = "updated" if metadata else "downloaded"
    detail = f"{target.relative_to(ROOT)} @ {resolved_commit} ({copied_files} files, {total_bytes} bytes)"
    if skipped:
        detail += f"; excluded {len(skipped)} files"
    return action, detail, True


def write_report(path: Path, source_date: str, batch: str, results: list[tuple[str, str, str]]) -> bool:
    lines = [
        f"# 源码导入报告：{source_date} {batch}",
        "",
        "此报告由 GitHub Actions 生成。导入的是受限源码快照，不执行第三方代码。",
        "",
        "| 项目 | 状态 | 目录或原因 |",
        "| --- | --- | --- |",
    ]
    for project, status, detail in results:
        lines.append(f"| `{project}` | {status} | `{detail.replace('|', '\\|')}` |")
    content = "\n".join(lines) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    manifests, load_errors = load_manifests()
    errors = list(load_errors)
    changed = False
    imported_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    for manifest_path, manifest in manifests:
        source_date = str(manifest.get("source_date") or manifest_path.stem[:10])
        batch = str(manifest.get("batch") or "unspecified")
        results: list[tuple[str, str, str]] = []
        projects = manifest.get("projects", [])
        for project in projects:
            if not isinstance(project, dict) or project.get("download", True) is False:
                continue
            project_name = str(project.get("repository") or project.get("slug") or "unknown")
            try:
                status, detail, did_change = import_project(project, manifest_path, imported_at)
                results.append((project_name, status, detail))
                changed = changed or did_change
            except Exception as exc:  # report one bad project without losing the batch
                detail = str(exc).replace("\n", " ")
                results.append((project_name, "failed", detail))
                errors.append(f"{manifest_path.name} / {project_name}: {detail}")

        report_path = MANIFEST_DIR / f"{manifest_path.stem}-import-report.md"
        changed = write_report(report_path, source_date, batch, results) or changed

    for error in load_errors:
        print(f"ERROR: {error}", file=sys.stderr)
    for error in errors:
        if error not in load_errors:
            print(f"ERROR: {error}", file=sys.stderr)
    print(f"processed {len(manifests)} manifests; changed={changed}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
