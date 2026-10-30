"""Decryptor for the sportzx/playfy template API (SportzxCryptoUtils reimplementation)."""
import base64, hmac, hashlib
from Crypto.Cipher import AES

CHARSET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+!@#$%&='
M = 0xFFFFFFFF
CTX = bytes.fromhex('1676ec7db4771b0d826d70369b579684b182d2c0133be041bdd55f5d6d79a98b')
PRK = bytes.fromhex('d1a7ebbaed93b2f68ac092ade2b0075d917634447a3519b41e817ad631020053')
MAGIC = bytes([0xDE, 0xAD, 0xBE, 0xEF])
V3_PEPPER = bytes([177, 101, 125, 227, 9, 214, 231, 144, 96, 122, 92, 78, 231, 209, 175, 72,
                   83, 245, 113, 133, 125, 201, 101, 230, 92, 181, 103, 67, 146, 58, 69, 121])
V3_LABEL = b'SXR3/kdf'
CONSTS = [1398297139, (-1640531527) & M, 2101127200, (-1028477379) & M]


def u32(x): return x & 0xFFFFFFFF


def gen_key_iv(pw):
    b = pw.encode(); n = len(b)
    h = u32(2166136261)
    for ch in b: h = u32(((ch & 255) ^ h) * 16777619)
    k = bytearray(16)
    for i in range(16):
        h = u32(31 * h + (i ^ (b[i % n] & 255))); k[i] = CHARSET[h % len(CHARSET)]
    h = u32(2166129450)
    for ch in b: h = u32((((ch) & 255) ^ h) * 16777619)
    iv = bytearray(16); cnt = 0
    for i in range(0, 48, 3):
        h = u32(29 * h + (cnt ^ (b[i % n] & 255))); iv[i // 3] = CHARSET[h % len(CHARSET)]; cnt = u32(7 + cnt)
    return bytes(k), bytes(iv)


AES_KEY, AES_IV = gen_key_iv('oAR80SGuX3EEjUGFRwLFKBTiris=')


def ub64(s):
    s = s.strip().replace('-', '+').replace('_', '/')
    return base64.b64decode(s + '=' * (-len(s) % 4))


def rotr3(x): return ((x >> 3) | ((x << 5) & 0xFF)) & 0xFF


def postprocess(raw):
    return bytes(rotr3(b) ^ CTX[i % 32] for i, b in enumerate(raw))


def _rol(x, n): x &= M; return ((x << n) | (x >> (32 - n))) & M


def _qr(s, a, b, c, d):
    s[a] = (s[a] + s[b]) & M; s[d] = _rol(s[d] ^ s[a], 13)
    s[c] = (s[c] + s[d]) & M; s[b] = _rol(s[b] ^ s[c], 17)
    s[a] = (s[a] + s[b]) & M; s[d] = _rol(s[d] ^ s[a], 9)
    s[c] = (s[c] + s[d]) & M; s[b] = _rol(s[b] ^ s[c], 25)


def _permute(s):
    for _ in range(10):
        _qr(s, 0, 4, 8, 12); _qr(s, 1, 5, 9, 13); _qr(s, 2, 6, 10, 14); _qr(s, 3, 7, 11, 15)
        _qr(s, 0, 5, 10, 15); _qr(s, 1, 6, 11, 12); _qr(s, 2, 7, 8, 13); _qr(s, 3, 4, 9, 14)


def _ld(b, o): return b[o] | b[o + 1] << 8 | b[o + 2] << 16 | b[o + 3] << 24


class _Sponge:
    def __init__(self):
        self.state = [((-1640531527) * (i + 1)) & M for i in range(16)]
        self.buf = bytearray(32); self.pos = 0

    def absorb(self, data, n, off=0):
        for i in range(n):
            self.buf[self.pos] = data[off + i]; self.pos += 1
            if self.pos == 32:
                for j in range(8): self.state[j] ^= _ld(self.buf, j * 4)
                _permute(self.state); self.pos = 0

    def final(self):
        self.buf[self.pos] = 0x80; self.pos += 1
        while self.pos < 32: self.buf[self.pos] = 0; self.pos += 1
        for j in range(8): self.state[j] ^= _ld(self.buf, j * 4)
        _permute(self.state)
        out = bytearray(32)
        for j in range(8): out[j * 4:(j + 1) * 4] = self.state[j].to_bytes(4, 'little')
        return bytes(out)


def _prf(data):
    s = _Sponge(); s.absorb(data, len(data)); return s.final()


def _derive(ctx, nonce16):
    k0 = _prf(V3_LABEL + ctx + V3_PEPPER + nonce16)
    k1 = _prf(k0 + b'\x01'); k2 = _prf(k0 + b'\x02')
    return [_ld(k1, i * 4) for i in range(8)], k2


def _block(key, ctr, nonce3):
    v = list(CONSTS) + list(key) + [ctr] + list(nonce3)
    w = list(v); _permute(w)
    return b''.join(((w[i] + v[i]) & M).to_bytes(4, 'little') for i in range(16))


def dec_v3(blob):
    assert blob[0] == 3 and len(blob) >= 45, 'not v3'
    nonce, hdr = blob[1:17], [_ld(blob, 17 + i * 4) for i in range(3)]
    ct, tag = blob[29:-16], blob[-16:]
    key, k2 = _derive(CTX, nonce)
    s = _Sponge(); s.absorb(k2, 32); s.absorb(blob, 29); s.absorb(ct, len(ct)); s.absorb(k2, 32)
    assert s.final()[:16] == tag, 'tag mismatch'
    out = bytearray(); ctr = 0
    for off in range(0, len(ct), 64):
        ks = _block(key, ctr, hdr); ctr += 1
        chunk = ct[off:off + 64]
        out += bytes(c ^ k for c, k in zip(chunk, ks))
    return bytes(out).decode()


def dec_primary(blob):
    assert blob[:4] == MAGIC, 'bad magic'
    klen = blob[4]; ct = blob[5:len(blob) - klen] if klen else blob[5:]
    kb = blob[len(blob) - klen:] if klen else b''
    hk = kb + CTX
    out, prev, c = b'', b'', 1
    while len(out) < 48:
        prev = hmac.new(hk, prev + hk + bytes([c]), hashlib.sha256).digest()
        out += prev; c += 1
    pt = AES.new(out[:32], AES.MODE_CBC, out[32:48]).decrypt(ct)
    pt = pt[:-pt[-1]]
    return postprocess(pt).decode()


def dec_v2(blob):
    assert blob[0] == 2, 'not v2'
    iv, tag, ct = blob[1:17], blob[-32:], blob[17:-32]
    prk = hmac.new(b'sportzx/v2/prk', CTX, hashlib.sha256).digest()
    mk = hmac.new(prk, b'mac', hashlib.sha256).digest()
    ek = hmac.new(prk, b'enc', hashlib.sha256).digest()
    assert hmac.new(mk, blob[:-32], hashlib.sha256).digest() == tag, 'tag mismatch'
    pt = AES.new(ek, AES.MODE_CBC, iv).decrypt(ct)
    pt = pt[:-pt[-1]]
    return postprocess(pt).decode()


def dec_fallback2(blob):
    pt = AES.new(AES_KEY, AES.MODE_CBC, AES_IV).decrypt(blob)
    pad = pt[-1]
    return (pt[:-pad] if 1 <= pad <= 16 else pt).decode()


def decrypt_payload(raw):
    """Try every known scheme. Returns (scheme, text). Raises on failure."""
    blob = ub64(raw)
    errors = {}
    if blob[:4] == MAGIC:
        order = [('primary', dec_primary)]
    elif blob[0:1] == b'\x02':
        order = [('v2', dec_v2)]
    elif blob[0:1] == b'\x03':
        order = [('v3', dec_v3)]
    else:
        order = []
    order += [('fallback2', dec_fallback2)]
    for name, fn in order:
        try:
            t = fn(blob)
            if t.startswith(('{', '[')) or 'http' in t or 'youtu' in t:
                return name, t
            errors[name] = 'decoded but not structured: ' + t[:60]
        except Exception as e:
            errors[name] = str(e)[:70]
    raise ValueError('all schemes failed: %s' % errors)
