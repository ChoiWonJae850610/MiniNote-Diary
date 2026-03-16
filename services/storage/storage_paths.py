from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable

from services.common.field_keys import MaterialKeys, PayloadKeys
from services.common.project_paths import db_dir_path

_WINDOWS_INVALID = r'<>:"/\\|?*'
_VENDOR_SECTION_KEYS: tuple[str, ...] = (
    PayloadKeys.TRIMS,
    PayloadKeys.FABRICS,
    PayloadKeys.DYEINGS,
    PayloadKeys.FINISHINGS,
    PayloadKeys.OTHERS,
)
_DEFAULT_IMAGE_EXT = '.jpg'


def sanitize_filename_part(s: str, default: str = 'UNKNOWN', max_len: int = 60) -> str:
    s = (s or '').strip() or default
    s = re.sub(f'[{re.escape(_WINDOWS_INVALID)}]', '_', s)
    s = re.sub(r'\s+', ' ', s).strip().rstrip('.\n ').strip() or default
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    return s


def ensure_db_dir(base_dir: str | os.PathLike[str] | None = None) -> str:
    return str(db_dir_path(Path(base_dir) if base_dir is not None else None))


def make_base_filename(date_str: str, style_no: str, vendor_name: str) -> str:
    date_part = sanitize_filename_part(date_str, default='0000-00-00', max_len=20)
    style_part = sanitize_filename_part(style_no, default='NO_STYLE', max_len=40)
    vendor_part = sanitize_filename_part(vendor_name, default='NO_VENDOR', max_len=60)
    return f'{date_part}_{style_part}_{vendor_part}'


def first_vendor_in_rows(rows: Iterable[dict[str, Any]] | None) -> str:
    for row in rows or []:
        value = (row.get(MaterialKeys.VENDOR) or '').strip()
        if value:
            return value
    return ''


def iter_vendor_candidates(data: Dict[str, Any]) -> Iterable[str]:
    yield first_vendor_in_rows(data.get(PayloadKeys.TRIMS, []))
    yield first_vendor_in_rows(data.get(PayloadKeys.FABRICS, []))
    for row in data.get(PayloadKeys.FABRICS, []):
        legacy = (row.get(MaterialKeys.LEGACY_FABRIC_VENDOR) or '').strip()
        if legacy:
            yield legacy
    for section_key in _VENDOR_SECTION_KEYS[2:]:
        yield first_vendor_in_rows(data.get(section_key, []))


def pick_vendor_name(data: Dict[str, Any]) -> str:
    return next((value for value in iter_vendor_candidates(data) if value), 'NO_VENDOR')


def image_extension(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.lower() if ext else _DEFAULT_IMAGE_EXT


def unique_available_stem(db_dir: str | os.PathLike[str], base_name: str) -> str:
    db_path = Path(db_dir)
    candidate = sanitize_filename_part(base_name, default='UNTITLED', max_len=120)
    if not _stem_exists(db_path, candidate):
        return candidate
    index = 2
    while True:
        numbered = sanitize_filename_part(f'{base_name}_{index}', default='UNTITLED', max_len=120)
        if not _stem_exists(db_path, numbered):
            return numbered
        index += 1


def _stem_exists(db_path: Path, stem: str) -> bool:
    for ext in ('.json', '.png', '.jpg', '.jpeg', '.bmp'):
        if (db_path / f'{stem}{ext}').exists():
            return True
    return False
