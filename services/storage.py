import base64
import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


_WINDOWS_INVALID = r'<>:"/\\|?*'


def _sanitize_filename_part(s: str, default: str = "UNKNOWN", max_len: int = 60) -> str:
    s = (s or "").strip()
    if not s:
        s = default
    s = re.sub(f"[{re.escape(_WINDOWS_INVALID)}]", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.rstrip(". ").strip()
    if not s:
        s = default
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    return s


def _canonical_json_bytes(obj: Any) -> bytes:
    # 로드/해시/암호화를 위해 canonical 형태로 직렬화
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ensure_db_dir(base_dir: str) -> str:
    db_dir = os.path.join(base_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    return db_dir


def make_base_filename(date_str: str, style_no: str, vendor_name: str) -> str:
    date_part = _sanitize_filename_part(date_str, default="0000-00-00", max_len=20)
    style_part = _sanitize_filename_part(style_no, default="NO_STYLE", max_len=40)
    vendor_part = _sanitize_filename_part(vendor_name, default="NO_VENDOR", max_len=60)
    return f"{date_part}_{style_part}_{vendor_part}"


def pick_vendor_name(data: Dict[str, Any]) -> str:
    trims = data.get("trims", [])
    for row in trims:
        v = (row.get("거래처") or "").strip()
        if v:
            return v
    fabrics = data.get("fabrics", [])
    for row in fabrics:
        v = (row.get("원단처") or "").strip()
        if v:
            return v
    return "NO_VENDOR"


def _key_path(db_dir: str) -> str:
    return os.path.join(db_dir, ".key")


def get_or_create_key(db_dir: str) -> bytes:
    """
    AES-256 key (32 bytes)
    - 현재는 db/.key 파일에 저장 (메모장으로 봐도 의미 없는 base64)
    - 추후 보안을 올리려면 Windows DPAPI로 보호하는 방식으로 변경 권장
    """
    kp = _key_path(db_dir)
    if os.path.isfile(kp):
        with open(kp, "rb") as f:
            b64 = f.read().strip()
        return base64.b64decode(b64)

    key = os.urandom(32)
    with open(kp, "wb") as f:
        f.write(base64.b64encode(key))
    return key


def encrypt_data(db_dir: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    반환: JSON에 저장할 암호화 payload (평문 데이터 없음)
    """
    key = get_or_create_key(db_dir)
    aes = AESGCM(key)

    plaintext = _canonical_json_bytes(data)
    nonce = os.urandom(12)  # AESGCM nonce 12 bytes 권장

    ciphertext = aes.encrypt(nonce, plaintext, associated_data=None)

    return {
        "enc": {
            "alg": "AES-256-GCM",
            "nonce_b64": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext_b64": base64.b64encode(ciphertext).decode("utf-8"),
        },
        # 무결성/검증 용도(평문 SHA256)
        "sha256_plain": sha256_bytes(plaintext),
    }


def decrypt_payload(db_dir: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    추후 로드 구현 시 사용 (복호화)
    """
    key = get_or_create_key(db_dir)
    aes = AESGCM(key)

    enc = payload["enc"]
    nonce = base64.b64decode(enc["nonce_b64"])
    ciphertext = base64.b64decode(enc["ciphertext_b64"])

    plaintext = aes.decrypt(nonce, ciphertext, associated_data=None)
    data = json.loads(plaintext.decode("utf-8"))

    # 검증
    expected = payload.get("sha256_plain", "")
    actual = sha256_bytes(_canonical_json_bytes(data))
    if expected and expected != actual:
        raise ValueError("무결성 검증 실패: 파일이 변조되었을 수 있습니다.")

    return data


def save_work_order(
    base_dir: str,
    data: Dict[str, Any],
    image_src_path: Optional[str] = None,
) -> Tuple[str, Optional[str], str]:
    """
    Returns: (json_path, image_path_or_None, sha256_plain)
    JSON 파일에는 평문이 저장되지 않고 enc(ciphertext)만 저장됨.
    """
    db_dir = ensure_db_dir(base_dir)

    header = data.get("header", {})
    date_str = str(header.get("date", "") or "")
    style_no = str(header.get("style_no", "") or "")

    vendor_name = pick_vendor_name(data)
    base_name = make_base_filename(date_str, style_no, vendor_name)

    enc_payload = encrypt_data(db_dir, data)

    payload = {
        "version": 1,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        **enc_payload,
    }

    json_path = os.path.join(db_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    # 이미지 복사(있으면)
    image_dst_path = None
    if image_src_path and os.path.isfile(image_src_path):
        _, ext = os.path.splitext(image_src_path)
        ext = ext.lower() if ext else ".jpg"
        image_dst_path = os.path.join(db_dir, f"{base_name}{ext}")
        shutil.copy2(image_src_path, image_dst_path)

    return json_path, image_dst_path, payload["sha256_plain"]