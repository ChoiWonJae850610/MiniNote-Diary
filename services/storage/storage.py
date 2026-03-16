import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from services.common.field_keys import PayloadKeys
from services.storage.storage_crypto import decrypt_payload, encrypt_data, sha256_bytes
from services.storage.storage_paths import ensure_db_dir, image_extension, make_base_filename, pick_vendor_name, unique_available_stem

_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp')


def _build_payload(data: Dict[str, Any], enc_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        PayloadKeys.VERSION: 1,
        PayloadKeys.SAVED_AT: datetime.now().isoformat(timespec='seconds'),
        **enc_payload,
    }


def _same_path(left: str, right: str) -> bool:
    try:
        return os.path.samefile(left, right)
    except Exception:
        return os.path.abspath(left) == os.path.abspath(right)


def _find_existing_image(existing_prefix: str) -> Optional[str]:
    for ext in _IMAGE_EXTENSIONS:
        candidate = f'{existing_prefix}{ext}'
        if os.path.isfile(candidate):
            return candidate
    return None


def save_work_order(
    base_dir: str | None,
    data: Dict[str, Any],
    image_src_path: Optional[str] = None,
    overwrite_template_id: Optional[str] = None,
) -> Tuple[str, Optional[str], str]:
    db_dir = ensure_db_dir(base_dir)
    header = data.get(PayloadKeys.HEADER, {})
    base_name = make_base_filename(
        str(header.get('date', '') or ''),
        str(header.get('style_no', '') or ''),
        pick_vendor_name(data),
    )
    unique_name = overwrite_template_id or unique_available_stem(db_dir, base_name)

    payload = _build_payload(data, encrypt_data(db_dir, data))
    json_path = os.path.join(db_dir, f'{unique_name}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    image_dst_path = None
    existing_prefix = os.path.join(db_dir, unique_name)
    existing_image_path = _find_existing_image(existing_prefix) if overwrite_template_id else None

    keep_existing_image = bool(
        overwrite_template_id
        and image_src_path
        and existing_image_path
        and os.path.isfile(image_src_path)
        and _same_path(image_src_path, existing_image_path)
    )

    if overwrite_template_id and existing_image_path and not keep_existing_image:
        for ext in _IMAGE_EXTENSIONS:
            existing_image = f'{existing_prefix}{ext}'
            if os.path.isfile(existing_image):
                try:
                    os.remove(existing_image)
                except OSError:
                    pass

    if keep_existing_image:
        image_dst_path = existing_image_path
    elif image_src_path and os.path.isfile(image_src_path):
        image_dst_path = os.path.join(db_dir, f'{unique_name}{image_extension(image_src_path)}')
        if not _same_path(image_src_path, image_dst_path):
            shutil.copy2(image_src_path, image_dst_path)
        else:
            image_dst_path = image_src_path

    return json_path, image_dst_path, payload['sha256_plain']


__all__ = ['decrypt_payload', 'ensure_db_dir', 'save_work_order', 'sha256_bytes']
