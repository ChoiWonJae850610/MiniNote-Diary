from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.common.project_paths import db_dir_path


@dataclass(frozen=True)
class DbResetResult:
    deleted_count: int


class DbResetService:
    _PROTECTED_FILENAMES: tuple[str, ...] = ('.key',)

    @classmethod
    def reset_all(cls, base_dir: str | Path | None = None) -> DbResetResult:
        db_dir = db_dir_path(base_dir)
        deleted_count = 0
        for path in db_dir.iterdir():
            if not path.is_file():
                continue
            if path.name in cls._PROTECTED_FILENAMES:
                continue
            path.unlink(missing_ok=True)
            deleted_count += 1
        return DbResetResult(deleted_count=deleted_count)
