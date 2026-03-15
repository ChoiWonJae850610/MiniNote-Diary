from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any, Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def key_path(db_dir: str) -> str:
    return os.path.join(db_dir, '.key')


def get_or_create_key(db_dir: str) -> bytes:
    path = key_path(db_dir)
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return base64.b64decode(f.read().strip())
    key = os.urandom(32)
    with open(path, 'wb') as f:
        f.write(base64.b64encode(key))
    return key


def encrypt_data(db_dir: str, data: Dict[str, Any]) -> Dict[str, Any]:
    aes = AESGCM(get_or_create_key(db_dir))
    plaintext = canonical_json_bytes(data)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plaintext, associated_data=None)
    return {
        'enc': {
            'alg': 'AES-256-GCM',
            'nonce_b64': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext_b64': base64.b64encode(ciphertext).decode('utf-8'),
        },
        'sha256_plain': sha256_bytes(plaintext),
    }


def decrypt_payload(db_dir: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    aes = AESGCM(get_or_create_key(db_dir))
    enc = payload['enc']
    plaintext = aes.decrypt(
        base64.b64decode(enc['nonce_b64']),
        base64.b64decode(enc['ciphertext_b64']),
        associated_data=None,
    )
    data = json.loads(plaintext.decode('utf-8'))
    expected = payload.get('sha256_plain', '')
    actual = sha256_bytes(canonical_json_bytes(data))
    if expected and expected != actual:
        raise ValueError('무결성 검증 실패: 파일이 변조되었을 수 있습니다.')
    return data
