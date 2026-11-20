"""Pure-python Keccak-256 (original Keccak padding 0x01...0x80, NOT NIST SHA3).
Fallback for eth_hash backend missing (pycryptodome/pysha3 not installed).
Self-tests on import against known vectors.
"""
_MASK = (1 << 64) - 1
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
        0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
        0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
        0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
        0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_R = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
      [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
_PILN = [10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4, 15, 23, 19, 13, 12, 2, 20, 14, 22, 9, 6, 1]


def _rol(x, n):
    return ((x << n) | (x >> (64 - n))) & _MASK


def _keccak_f(st):
    for rc in _RC:
        c = [st[x] ^ st[x + 5] ^ st[x + 10] ^ st[x + 15] ^ st[x + 20] for x in range(5)]
        d = [c[(x + 4) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
        st = [st[i] ^ d[i % 5] for i in range(25)]
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = _rol(st[x + 5 * y], _R[x][y])
        st = [b[i] ^ ((~b[(i // 5) * 5 + ((i % 5) + 1) % 5]) & b[(i // 5) * 5 + ((i % 5) + 2) % 5])
              for i in range(25)]
        st[0] ^= rc
    return st


def keccak256(data: bytes) -> bytes:
    b = bytearray(data)
    b.append(0x01)
    while len(b) % 136 != 135:
        b.append(0)
    b.append(0x80)
    st = [0] * 25
    for off in range(0, len(b), 136):
        blk = b[off:off + 136]
        for i in range(17):
            st[i] ^= int.from_bytes(blk[8 * i:8 * i + 8], "little")
        st = _keccak_f(st)
    return b"".join(st[i].to_bytes(8, "little") for i in range(4))


def selector(sig: str) -> str:
    return keccak256(sig.encode()).hex()


# Self-test on import: known Keccak-256 vectors.
assert keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470", "keccak empty vector failed"
assert keccak256(b"hello").hex() == "1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8", "keccak hello vector failed"
