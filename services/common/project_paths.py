from __future__ import annotations

from pathlib import Path

_PROJECT_MARKERS: tuple[str, ...] = ('main.py', 'db', 'services', 'ui')


def resolve_project_root(anchor: str | Path | None = None) -> Path:
    current = Path(anchor) if anchor is not None else Path(__file__)
    current = current.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in _PROJECT_MARKERS):
            return candidate
    raise RuntimeError(f'Could not resolve project root from: {current}')


def project_root_path(anchor: str | Path | None = None) -> Path:
    return resolve_project_root(anchor)


def db_dir_path(anchor: str | Path | None = None) -> Path:
    path = resolve_project_root(anchor) / 'db'
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_file_path(filename: str, anchor: str | Path | None = None) -> Path:
    return db_dir_path(anchor) / filename


def project_root_str(anchor: str | Path | None = None) -> str:
    return str(project_root_path(anchor))


def db_dir_str(anchor: str | Path | None = None) -> str:
    return str(db_dir_path(anchor))
