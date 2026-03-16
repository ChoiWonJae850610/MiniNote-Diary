import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from services.common.field_keys import PayloadKeys
from services.storage.storage_crypto import decrypt_payload, encrypt_data, sha256_bytes
from services.storage.storage_paths import ensure_db_dir, image_extension, make_base_filename, pick_vendor_name


def _build_payload(data: Dict[str, Any], enc_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        PayloadKeys.VERSION: 1,
        PayloadKeys.SAVED_AT: datetime.now().isoformat(timespec='seconds'),
        **enc_payload,
    }


def save_work_order(
    base_dir: str,
    data: Dict[str, Any],
    image_src_path: Optional[str] = None,
) -> Tuple[str, Optional[str], str]:
    db_dir = ensure_db_dir(base_dir)
    header = data.get(PayloadKeys.HEADER, {})
    base_name = make_base_filename(
        str(header.get('date', '') or ''),
        str(header.get('style_no', '') or ''),
        pick_vendor_name(data),
    )

    payload = _build_payload(data, encrypt_data(db_dir, data))
    json_path = os.path.join(db_dir, f'{base_name}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    image_dst_path = None
    if image_src_path and os.path.isfile(image_src_path):
        image_dst_path = os.path.join(db_dir, f'{base_name}{image_extension(image_src_path)}')
        shutil.copy2(image_src_path, image_dst_path)

    return json_path, image_dst_path, payload['sha256_plain']


__all__ = ['decrypt_payload', 'ensure_db_dir', 'save_work_order', 'sha256_bytes']
