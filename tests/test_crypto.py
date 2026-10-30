"""Crypto tests — decrypt live-captured blobs with the ported SportzxCryptoUtils."""
import json
from pathlib import Path

from cancha.api.crypto import decrypt_payload

FIX = Path(__file__).parent / "fixtures"


def _blob(name):
    raw = json.loads((FIX / name).read_text())["data"]
    assert isinstance(raw, str) and raw
    return raw


def test_channel_file_decrypts_to_json():
    scheme, text = decrypt_payload(_blob("ch1.json"))
    assert scheme in ("v3", "fallback2", "primary", "v2")
    parsed = json.loads(text)
    assert isinstance(parsed, (dict, list))


def test_highlight_file_decrypts_to_json():
    scheme, text = decrypt_payload(_blob("hl27.json"))
    assert scheme in ("v3", "fallback2", "primary", "v2")
    parsed = json.loads(text)
    assert isinstance(parsed, (dict, list))


def test_tiny_blob_decrypts():
    scheme, text = decrypt_payload(_blob("cricket.json"))
    assert isinstance(text, str) and len(text) > 0
