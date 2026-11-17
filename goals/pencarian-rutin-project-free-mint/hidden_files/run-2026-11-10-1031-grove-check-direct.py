#!/usr/bin/env python3
"""Agent Grove fase 2 watch — run 2026-11-10 10:31 WIB, direct fallback.
Read-only. fast_rpc race (8s timeout) gagal di semua endpoint karena jaringan
VM sangat lambat (curl 25s ke dataseed Binance BERHASIL menjawab
eth_blockNumber). Fallback ini pakai timeout 30s per endpoint; selector
tetap dihitung keccak saat runtime — tanpa calldata ketik tangan.
"""
import json
import time
import urllib.request

from Crypto.Hash import keccak

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ENDPOINTS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed3.bnbchain.org",
    "https://bsc-dataseed4.bnbchain.org",
    "https://bsc-dataseed-public.bnbchain.org",
]


def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]


def enc(addr):
    return addr[2:].lower().rjust(64, "0")


def rpc(url, method, params, timeout=30):
    body = json.dumps(
        {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def try_all(method, params):
    errs = []
    for url in ENDPOINTS:
        try:
            res = rpc(url, method, params)
            if "result" in res:
                return url, res["result"]
            errs.append(f"{url}: {res.get('error')}")
        except Exception as e:  # noqa: BLE001
            errs.append(f"{url}: {type(e).__name__}")
    raise IOError("all endpoints failed: " + "; ".join(errs))


t0 = time.time()
url, block_hex = try_all("eth_blockNumber", [])
block = int(block_hex, 16)
_, free_open_hex = try_all(
    "eth_call", [{"to": GROVE, "data": sel("freeOpen()")}, "latest"]
)
_, free_claimed_hex = try_all(
    "eth_call",
    [{"to": GROVE, "data": sel("freeClaimed(address)") + enc(USER)}, "latest"],
)
out = {
    "run": "2026-11-10 10:31 WIB",
    "status": "ok",
    "block": block,
    "freeOpen": int(free_open_hex, 16),
    "freeClaimed_user": bool(int(free_claimed_hex, 16)),
    "endpoint_used": url,
    "elapsed_s": round(time.time() - t0, 2),
    "note": (
        "fast_rpc race (8s) gagal 3x krn jaringan VM sangat lambat; "
        "fallback direct timeout 30s berhasil. Bukan perubahan state."
    ),
}
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-1031-grove-check.json", "w"), indent=1)
